# GITAMW Python Smart IDE — Installation & Deployment Guide

**Department of Computer Science and Engineering**  
**Gouthami Institute of Technology for Women (Autonomous), Proddatur**

---

## 1. System Requirements

- **Operating System**: Windows 10 / 11 (64-bit)
- **Python Version**: Python 3.9, 3.10, 3.11, or 3.12 (64-bit)
- **RAM**: Minimum 2 GB (4 GB recommended)
- **Storage**: 150 MB free disk space

---

## 2. Building the Windows Installer Executable (.exe)

To package the entire Python IDE into a single standalone Windows executable (`GITAMW_Smart_IDE.exe`) for computer lab deployment:

### Step 1: Install Build Requirements
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Execute PyInstaller Automated Build
Run the automated build script:
```bash
python installer/pyinstaller_build.py
```

### Step 3: Locate Executable
Once the build process completes, your standalone executable will be located at:
`installer/dist/GITAMW_Smart_IDE.exe`

### Step 4: Lab Deployment
Copy `GITAMW_Smart_IDE.exe` to any Windows computer in the GITAMW CSE Computer Laboratories. Double-clicking the `.exe` will launch the FastAPI background server and open the browser IDE window without requiring command prompts or internet access.

---
