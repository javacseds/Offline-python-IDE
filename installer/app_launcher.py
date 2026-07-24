"""
GITAMW Python Smart IDE - Windows Executable Launcher
======================================================
Gouthami Institute of Technology and Management for Women (Autonomous)
Department of Computer Science & Engineering

Features:
  - Starts FastAPI/Uvicorn server silently (no console window)
  - Waits for server readiness, then auto-opens browser
  - System tray icon with Quit option
  - Single instance guard (prevents double-launch)
  - Graceful shutdown on exit
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
import ctypes

# ─── PyInstaller frozen bundle support ───────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    APP_DIR  = os.path.dirname(sys.executable)   # folder where .exe lives
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR  = BASE_DIR

sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)          # ensure relative paths inside FastAPI resolve correctly


# ─── Single-Instance Guard ─────────────────────────────────────────────────
MUTEX_NAME = "GITAMW_Python_Smart_IDE_Mutex_v1"
_mutex = None

def acquire_single_instance():
    """Return True if this is the first instance, False if already running."""
    global _mutex
    _mutex = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    return ctypes.windll.kernel32.GetLastError() != 183   # 183 = ERROR_ALREADY_EXISTS

def bring_existing_to_front(url):
    """If another instance is running, just open the browser to it."""
    try:
        webbrowser.open(url)
    except Exception:
        pass


# ─── Port Discovery ────────────────────────────────────────────────────────
def find_free_port(preferred: int = 8000) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


# ─── Server Readiness Check ────────────────────────────────────────────────
def wait_for_server(host: str, port: int, timeout: float = 20.0):
    """Block until the TCP port is open (server ready) or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.3)
    return False


# ─── System Tray Icon (optional — degrades gracefully if pystray missing) ──
def run_tray_icon(app_name: str, quit_event: threading.Event):
    try:
        import pystray
        from PIL import Image, ImageDraw

        # Draw a simple Python-orange circle icon
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, 60, 60], fill="#1e3a8a")
        draw.text((16, 18), "Py", fill="white")

        def on_quit(icon, item):
            icon.stop()
            quit_event.set()

        def on_open(icon, item):
            webbrowser.open(_server_url)

        menu = pystray.Menu(
            pystray.MenuItem("Open GITAMW IDE", on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit),
        )
        icon = pystray.Icon(app_name, img, app_name, menu)
        icon.run()
    except ImportError:
        # pystray not available – just wait for quit_event
        quit_event.wait()


# ─── Main Entry ────────────────────────────────────────────────────────────
_server_url = "http://127.0.0.1:8000"

def main():
    global _server_url

    port = find_free_port(8000)
    _server_url = f"http://127.0.0.1:{port}"

    # Single-instance check
    if not acquire_single_instance():
        bring_existing_to_front(_server_url)
        return

    # Import FastAPI app (after sys.path and chdir are set)
    from app.main import app as fastapi_app
    import uvicorn

    quit_event = threading.Event()

    # ── Start uvicorn in a daemon thread (no console window) ──
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

    # ── Wait for server then open browser ──
    def browser_launcher():
        if wait_for_server("127.0.0.1", port, timeout=25.0):
            webbrowser.open(_server_url)

    threading.Thread(target=browser_launcher, daemon=True).start()

    # ── System tray keeps app alive (blocking) ──
    run_tray_icon("GITAMW Python Smart IDE", quit_event)


if __name__ == "__main__":
    main()
