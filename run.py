"""
GITAMW Python Smart IDE - Local Runner
Gowthami Institute of Technology and Management for Women (Autonomous), Proddatur
"""
import sys
import uvicorn
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting GITAMW Python Smart IDE (Offline Edition)...")
    print(" College: Gowthami Institute of Technology and Management for Women (Autonomous), Proddatur")
    print("=" * 60)
    
    # Auto-open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
