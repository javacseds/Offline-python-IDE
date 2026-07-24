"""
GITAMW Python Smart IDE - Windows Executable Launcher Entry Point
Compiles into GITAMW_Smart_IDE.exe via PyInstaller.
"""
import os
import sys
import time
import socket
import webbrowser
import threading
import uvicorn

# Resolve bundle directory for PyInstaller frozen executable
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

from app.main import app

def find_free_port(default_port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', default_port))
            return default_port
        except OSError:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

def launch_browser(url):
    time.sleep(1.2)
    webbrowser.open(url)

if __name__ == '__main__':
    port = find_free_port(8000)
    server_url = f"http://127.0.0.1:{port}"
    
    # Launch browser thread
    threading.Thread(target=launch_browser, args=(server_url,), daemon=True).start()
    
    # Run Uvicorn Server
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
