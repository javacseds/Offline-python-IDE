"""
GITAMW Python Smart IDE - Local Runner
Gowthami Institute of Technology and Management for Women (Autonomous), Proddatur
"""
import sys
import time
import socket
import threading
import webbrowser
import uvicorn

def find_free_port(preferred: int = 8000) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.25)
    return False

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting GITAMW Python Smart IDE (Offline Edition)...")
    print(" College: Gowthami Institute of Technology and Management for Women (Autonomous), Proddatur")
    print("=" * 60)
    
    port = find_free_port(8000)
    server_url = f"http://127.0.0.1:{port}"

    def launch_browser():
        if wait_for_server("127.0.0.1", port, timeout=15.0):
            print(f"\n[OK] Server is ready at {server_url}. Opening browser...")
            webbrowser.open(server_url)
        else:
            print(f"\n[ERR] Server failed to start on 127.0.0.1:{port} after 15s timeout.")

    threading.Thread(target=launch_browser, daemon=True).start()
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
