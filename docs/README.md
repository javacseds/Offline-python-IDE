# GITAMW Python Smart IDE (Offline Edition)

**Gouthami Institute of Technology for Women (Autonomous), Proddatur**  
*Department of Computer Science and Engineering*

---

## Overview

**GITAMW Python Smart IDE** is a production-ready, completely offline desktop Python IDE designed specifically for B.Tech students, faculty, and lab instructors. It combines the interactive code execution of **Jupyter Notebook**, the editing power of **VS Code**, and the user accessibility of **Google Colab** into a single offline Windows application.

---

## Key Features

- **100% Offline Architecture**: Zero internet required. No cloud, no online database, no external API tracking.
- **Glassmorphism Animated Login**: Student profile validation (Name, Roll Number, Branch, Year, Semester, Section) stored locally in JSON.
- **3-Second Animated Splash Screen**: Featuring GITAMW Branding & Python Logo animation.
- **VS Code Monaco Editor**: Syntax highlighting, auto-completion, line numbers, search/replace, word wrap, and keyboard shortcuts (`F5` or `Ctrl+Enter` to run, `Ctrl+S` to save, `Ctrl+L` to clear console).
- **Smart Error Explainer**: Intercepts Python exceptions (`SyntaxError`, `NameError`, `IndentationError`, `ZeroDivisionError`, `ImportError`, etc.) and translates raw tracebacks into beginner-friendly plain English with actionable suggestions.
- **Graphical Matplotlib Renderer**: Automatically captures rendered Matplotlib charts (`plt.show()`) and presents them directly in the IDE Output Window.
- **Pip Package Manager**: Detects installed data science libraries (NumPy, Pandas, Matplotlib, Scikit-learn, PyTorch, OpenCV, etc.) and allows one-click `!pip install <package>` commands.
- **HTML & PDF Execution Reports**: Download complete student assignment reports with source code, output, runtime telemetry (seconds & MB RAM consumed), and Smart Error analysis.
- **Pre-loaded GITAMW Lab Programs**: Includes 11 ready-to-run CSE lab experiments ranging from basic variables to OOP, File I/O, NumPy, Pandas, and Matplotlib.

---

## Application Structure

```
d:/offline_python_interface/
├── app/
│   ├── main.py                 # FastAPI Web Server & REST API endpoints
│   ├── execution_engine.py     # Subprocess code runner & Matplotlib plot interceptor
│   ├── smart_error_explainer.py# AI/Rule-based beginner error explainer
│   ├── package_manager.py      # Local pip package manager & status checker
│   ├── storage_manager.py      # Local JSON database (students.json, history.json)
│   ├── file_manager.py         # Workspace file manager & report generator
│   ├── static/                 # Embedded CSS, JavaScript & Fonts
│   └── templates/              # HTML single page template
├── data/                       # Local JSON storage folder
├── saved_programs/             # Student saved scripts directory
├── sample_programs/            # CSE Lab sample experiments
├── installer/                  # PyInstaller executable build files
└── docs/                       # Comprehensive documentation suite
```

---

## Quick Start (Local Run)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Application**:
   ```bash
   python run.py
   ```
   The browser will automatically open to `http://127.0.0.1:8000` with the 3-second animated splash screen!

---
