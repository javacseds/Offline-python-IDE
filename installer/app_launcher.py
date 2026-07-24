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
  - Graceful shutdown
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

# ─── PyInstaller frozen bundle support ───────────────────────────────────────
if getattr(sys, "frozen", False):
    # _MEIPASS = temp dir where the bundle was extracted (onefile) or _internal (onedir)
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    # EXE_PATH = actual .exe location (persists, used for shortcuts & data storage)
    EXE_PATH = sys.executable
    EXE_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXE_PATH = os.path.abspath(__file__)
    EXE_DIR  = BASE_DIR

# Make sure all relative imports in the app resolve correctly
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)   # critical: ensures FastAPI template/static relative paths work


# ─── Single-Instance Guard ────────────────────────────────────────────────────
MUTEX_NAME = "GITAMW_Python_Smart_IDE_Mutex_v1"
_mutex_handle = None

def acquire_single_instance() -> bool:
    global _mutex_handle
    _mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    return ctypes.windll.kernel32.GetLastError() != 183  # 183 = ERROR_ALREADY_EXISTS


# ─── First-Run Flag ───────────────────────────────────────────────────────────
def is_first_run() -> bool:
    flag_file = os.path.join(EXE_DIR, ".gitamw_installed")
    return not os.path.exists(flag_file)

def mark_installed():
    flag_file = os.path.join(EXE_DIR, ".gitamw_installed")
    try:
        with open(flag_file, "w") as f:
            json.dump({"installed_at": time.strftime("%Y-%m-%d %H:%M:%S"), "version": "1.0.0"}, f)
    except Exception:
        pass


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
    except Exception:
        pass  # Shortcuts are optional; don't crash the app


# ─── Port Discovery ────────────────────────────────────────────────────────────
def find_free_port(preferred: int = 8000) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


# ─── Wait for Server Ready ─────────────────────────────────────────────────────
def wait_for_server(host: str, port: int, timeout: float = 30.0) -> bool:
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

        # Build icon image
        sz = 64
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)
        d.ellipse([2, 2, sz - 2, sz - 2], fill="#1e3a8a")
        # Orange inner circle
        margin = sz // 5
        d.ellipse([margin, margin, sz - margin, sz - margin], fill="#f97316")
        # Small white dot
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
        # pystray not bundled — just block until quit
        quit_event.wait()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    # 1. Single instance guard
    if not acquire_single_instance():
        # Another instance already running — just open the browser to it
        webbrowser.open(f"http://127.0.0.1:8000")
        return

    # 2. First-run setup: create shortcuts
    if is_first_run():
        create_shortcuts()
        mark_installed()

    # 3. Find port
    port       = find_free_port(8000)
    server_url = f"http://127.0.0.1:{port}"

    # 4. Import FastAPI app (AFTER chdir and sys.path are set)
    from app.main import app as fastapi_app
    import uvicorn

    quit_event = threading.Event()

    # 5. Start uvicorn in background thread (silent, no console)
    def run_server():
        uvicorn.run(
            fastapi_app,
            host="127.0.0.1",
            port=port,
            log_level="error",
            access_log=False,
        )

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 6. Wait for server ready, then open browser
    def open_browser():
        if wait_for_server("127.0.0.1", port, timeout=30.0):
            webbrowser.open(server_url)

    threading.Thread(target=open_browser, daemon=True).start()

    # 7. Show system tray icon (keeps app alive until user quits)
    run_tray_icon(quit_event, server_url)


if __name__ == "__main__":
    main()
