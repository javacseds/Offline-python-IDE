"""
One-Click PyInstaller Build Automation Script
Generates standalone Windows Desktop executable GITAMW_Smart_IDE.exe
"""
import os
import sys
import subprocess

def run_build():
    installer_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(installer_dir, "gitamw_ide.spec")
    
    print("=" * 65)
    print(" Building GITAMW Python Smart IDE Windows Executable...")
    print(" Target: GITAMW_Smart_IDE.exe")
    print(" Spec file:", spec_path)
    print("=" * 65)
    
    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_path]
    res = subprocess.run(cmd, cwd=installer_dir)
    
    if res.returncode == 0:
        dist_exe = os.path.join(installer_dir, "dist", "GITAMW_Smart_IDE.exe")
        print("\n" + "=" * 65)
        print(" BUILD SUCCESSFUL!")
        print(f" Executable generated at: {dist_exe}")
        print(" Double-click the EXE to launch GITAMW Python Smart IDE!")
        print("=" * 65)
    else:
        print("\n❌ Build failed. Ensure PyInstaller is installed (`pip install pyinstaller`).")

if __name__ == "__main__":
    run_build()
