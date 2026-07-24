# GITAMW Python Smart IDE — Offline Edition

**Gouthami Institute of Technology and Management for Women (Autonomous), Proddatur**  
*Department of Computer Science & Engineering*

---

## Overview

A fully offline Python IDE desktop application built for GITAMW students. Features a **FastAPI** backend, **Monaco Editor** frontend (the same editor used in VS Code), local Python execution engine, smart error explainer, package manager, syllabus viewer, and customizable IDE settings — all running completely offline without internet dependency.

---

## Features

- ✅ **Student Login** — Name, Roll No, Branch, Year, Semester, Section
- ✅ **Monaco Editor** — Syntax highlighting, line numbers, themes
- ✅ **Local Python Execution** — Runs code securely using `subprocess`
- ✅ **Smart Error Explainer** — Beginner-friendly error messages
- ✅ **Plots & Visuals** — Matplotlib chart rendering in the browser
- ✅ **Execution History** — Per-session program history log
- ✅ **Save / Load Files** — Student workspace file management
- ✅ **PDF Report Export** — Download all executed programs as a PDF lab report
- ✅ **Package Manager** — List installed Python libraries
- ✅ **Syllabus Tab** — Upload & view latest syllabus PDF in-browser
- ✅ **Settings Tab** — Customize editor + console (font size, family, theme, color)
- ✅ **Resizable Console** — Drag to resize output panel
- ✅ **Completely Offline** — No internet required after setup

---

## Project Structure

```
offline_python_interface/
├── run.py                        # App entry point (uvicorn launcher)
├── requirements.txt              # Python dependencies
├── .gitignore
├── app/
│   ├── main.py                   # FastAPI application & all API routes
│   ├── templates/
│   │   └── index.html            # Single-page HTML (Splash + Login + IDE)
│   └── static/
│       ├── css/
│       │   └── style.css         # Master stylesheet
│       └── js/
│           ├── app.js            # Main IDE application logic
│           └── splash.js         # Splash screen & session management
├── workspace/
│   ├── student_files/            # Student-saved .py files (runtime)
│   └── sample_programs/          # Pre-loaded lab experiments
└── installer/
    └── app_launcher.py           # PyInstaller entry point for .exe build
```

---

## Setup & Run

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python run.py
```

Then open your browser and visit: **http://127.0.0.1:8000**

---

## Build as Windows Executable (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "GITAMW_Python_IDE" installer/app_launcher.py
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Frontend | HTML5, Vanilla CSS, Vanilla JS |
| Editor | Monaco Editor (CDN) |
| PDF Export | ReportLab |
| Packaging | PyInstaller |

---

## License

Internal use — Gouthami Institute of Technology and Management for Women (Autonomous), Proddatur.  
Design & Developed by **Department of Computer Science & Engineering**.
