"""
GITAMW Python Smart IDE - Self-Contained Windows Launcher
==========================================================
Gouthami Institute of Technology and Management for Women (Autonomous)
Department of Computer Science & Engineering

Features (single .exe, no installer needed):
  - On FIRST RUN: creates Desktop & Start Menu shortcuts automatically
  - Starts FastAPI server silently (NO console window)
  - Waits for server ready, then opens browser (same interface as localhost)
  - System tray icon: right-click -> Open / Quit
  - Single-instance guard (prevents duplicate launches)
  - Graceful shutdown & robust log file error reporting
"""

import os
import sys
import time
import json
import socket
import threading
import webbrowser
import subprocess
import ctypes
import traceback

class NullStream:
    def write(self, buf):
        pass
    def read(self, n=-1):
        return ""
    def readline(self, limit=-1):
        return ""
    def flush(self):
        pass
    def isatty(self):
        return False

if sys.stdout is None:
    sys.stdout = NullStream()
if sys.stderr is None:
    sys.stderr = NullStream()
if sys.stdin is None:
    sys.stdin = NullStream()

UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "ERROR"},
        "uvicorn.error": {"level": "ERROR"},
        "uvicorn.access": {"handlers": ["default"], "level": "ERROR", "propagate": False},
    },
}

# ─── 0. Worker Process Mode (--run-script) ───────────────────────────────────
# When ExecutionEngine runs code in frozen mode, it invokes sys.executable with
# --run-script <path>. Handle this BEFORE any UI or server setup.
if len(sys.argv) > 1 and sys.argv[1] == "--run-script":
    try:
        import runpy
        script_path = sys.argv[2]
        sys.argv = [script_path]
        runpy.run_path(script_path, run_name="__main__")
        sys.exit(0)
    except Exception as exc:
        traceback.print_exc()
        sys.exit(1)


# ─── PyInstaller frozen bundle support ───────────────────────────────────────
if getattr(sys, "frozen", False):
    # _MEIPASS = temp dir where the bundle was extracted (onefile) or _internal (onedir)
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    EXE_PATH = sys.executable
    EXE_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXE_PATH = os.path.abspath(__file__)
    EXE_DIR  = BASE_DIR

# Make sure all relative imports in the app resolve correctly
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)   # critical: ensures FastAPI template/static relative paths work


# ─── Writable Root & Log File Resolution ─────────────────────────────────────
def get_writable_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        test_file = os.path.join(exe_dir, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return exe_dir
        except Exception:
            appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
            target_dir = os.path.join(appdata, "GITAMW_Python_Smart_IDE")
            os.makedirs(target_dir, exist_ok=True)
            return target_dir
    else:
        return BASE_DIR

WRITABLE_DIR = get_writable_dir()
LOG_FILE     = os.path.join(WRITABLE_DIR, "gitamw_ide.log")

def log_message(msg: str):
    """Write timestamped diagnostic entry to gitamw_ide.log."""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass

def show_error_box(title: str, message: str):
    """Display a native Windows MessageBox for critical startup failures."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)  # MB_ICONERROR | MB_OK
    except Exception:
        print(f"[{title}] {message}")


# ─── Single-Instance Guard ────────────────────────────────────────────────────
MUTEX_NAME = "GITAMW_Python_Smart_IDE_Mutex_v1"
_mutex_handle = None

def acquire_single_instance() -> bool:
    global _mutex_handle
    _mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    return ctypes.windll.kernel32.GetLastError() != 183  # 183 = ERROR_ALREADY_EXISTS


# ─── First-Run Flag ───────────────────────────────────────────────────────────
def is_first_run() -> bool:
    flag_file = os.path.join(WRITABLE_DIR, ".gitamw_installed")
    return not os.path.exists(flag_file)

def mark_installed():
    flag_file = os.path.join(WRITABLE_DIR, ".gitamw_installed")
    try:
        with open(flag_file, "w") as f:
            json.dump({"installed_at": time.strftime("%Y-%m-%d %H:%M:%S"), "version": "1.0.0"}, f)
    except Exception as e:
        log_message(f"Warning: Could not write install flag file: {e}")


# ─── Create Shortcuts (PowerShell, no external deps) ─────────────────────────
def create_shortcuts():
    """Create Desktop and Start Menu shortcuts using Windows Shell COM via PowerShell."""
    try:
        desktop_path   = os.path.join(os.path.expanduser("~"), "Desktop")
        start_menu_dir = os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft", "Windows", "Start Menu", "Programs", "GITAMW Python Smart IDE"
        )
        os.makedirs(start_menu_dir, exist_ok=True)

        lnk_desktop    = os.path.join(desktop_path,   "GITAMW Python Smart IDE.lnk").replace("\\", "\\\\")
        lnk_start      = os.path.join(start_menu_dir, "GITAMW Python Smart IDE.lnk").replace("\\", "\\\\")
        target         = EXE_PATH.replace("\\", "\\\\")
        work_dir       = EXE_DIR.replace("\\", "\\\\")

        ps = f"""
$ws = New-Object -ComObject WScript.Shell

$s1 = $ws.CreateShortcut("{lnk_desktop}")
$s1.TargetPath    = "{target}"
$s1.WorkingDirectory = "{work_dir}"
$s1.Description   = "GITAMW Python Smart IDE - Offline Python IDE"
$s1.WindowStyle   = 1
$s1.Save()

$s2 = $ws.CreateShortcut("{lnk_start}")
$s2.TargetPath    = "{target}"
$s2.WorkingDirectory = "{work_dir}"
$s2.Description   = "GITAMW Python Smart IDE - Offline Python IDE"
$s2.WindowStyle   = 1
$s2.Save()
"""
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", ps],
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=15
        )
        log_message("Created Desktop and Start Menu shortcuts.")
    except Exception as e:
        log_message(f"Shortcut creation warning: {e}")


# ─── Port Discovery ────────────────────────────────────────────────────────────
def find_free_port(preferred: int = 8000) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            free_port = s.getsockname()[1]
            log_message(f"Preferred port {preferred} in use. Selected free port {free_port}.")
            return free_port


# ─── Wait for Server Ready ─────────────────────────────────────────────────────
def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.25)
    return False


# ─── System Tray Icon ─────────────────────────────────────────────────────────
def run_tray_icon(quit_event: threading.Event, server_url: str):
    """Show a system tray icon. Falls back to silent wait if pystray unavailable."""
    try:
        import pystray
        from PIL import Image, ImageDraw

        sz = 64
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)
        d.ellipse([2, 2, sz - 2, sz - 2], fill="#1e3a8a")
        margin = sz // 5
        d.ellipse([margin, margin, sz - margin, sz - margin], fill="#f97316")
        c = sz // 2
        r = sz // 8
        d.ellipse([c - r, c - r, c + r, c + r], fill="white")

        def on_open(icon, item):
            webbrowser.open(server_url)

        def on_quit(icon, item):
            icon.stop()
            quit_event.set()

        menu = pystray.Menu(
            pystray.MenuItem("Open GITAMW Python IDE", on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit),
        )
        tray = pystray.Icon("GITAMW Python Smart IDE", img, "GITAMW Python Smart IDE", menu)
        tray.run()

    except ImportError:
        log_message("Pystray not available; tray icon disabled.")
        quit_event.wait()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    log_message("=" * 60)
    log_message("GITAMW Python Smart IDE starting up...")
    log_message(f"BASE_DIR: {BASE_DIR}")
    log_message(f"EXE_PATH: {EXE_PATH}")
    log_message(f"WRITABLE_DIR: {WRITABLE_DIR}")

    # 1. Single instance guard
    if not acquire_single_instance():
        log_message("Another instance is already running. Opening browser tab...")
        webbrowser.open("http://127.0.0.1:8000")
        return

    # 2. First-run setup: create shortcuts
    if is_first_run():
        create_shortcuts()
        mark_installed()

    # 3. Find port
    port       = find_free_port(8000)
    server_url = f"http://127.0.0.1:{port}"

    # 4. Import FastAPI app (AFTER chdir and sys.path are set)
    server_error = None
    try:
        from app.main import app as fastapi_app
        import uvicorn
    except Exception as e:
        server_error = traceback.format_exc()
        log_message(f"FATAL: Import error loading app.main:\n{server_error}")
        show_error_box(
            "GITAMW Python IDE - Import Error",
            f"Failed to load application modules.\n\nError Details:\n{e}\n\nLog File:\n{LOG_FILE}"
        )
        return

    quit_event = threading.Event()

    # 5. Start uvicorn in background thread
    def run_server():
        nonlocal server_error
        try:
            log_message(f"Starting uvicorn server on 127.0.0.1:{port}...")
            uvicorn.run(
                fastapi_app,
                host="127.0.0.1",
                port=port,
                log_config=UVICORN_LOG_CONFIG,
                access_log=False,
            )
        except Exception:
            server_error = traceback.format_exc()
            log_message(f"FATAL: Uvicorn server crashed:\n{server_error}")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 6. Wait for server ready, then open browser
    log_message("Polling for server TCP readiness on 127.0.0.1...")
    if wait_for_server("127.0.0.1", port, timeout=15.0):
        log_message(f"Server successfully bound and listening at {server_url}. Opening browser...")
        webbrowser.open(server_url)
    else:
        err_detail = server_error if server_error else f"Timed out after 15s waiting for port {port} on 127.0.0.1."
        log_message(f"FATAL: Server readiness failed. Detail:\n{err_detail}")
        show_error_box(
            "GITAMW Python IDE - Server Startup Failed",
            f"The local Python server failed to start on port {port}.\n\n"
            f"Error details:\n{err_detail}\n\n"
            f"A detailed log is available at:\n{LOG_FILE}"
        )
        return

    # 7. Show system tray icon (keeps app alive until user quits)
    run_tray_icon(quit_event, server_url)


if __name__ == "__main__":
    main()
