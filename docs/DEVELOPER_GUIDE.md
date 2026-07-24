# GITAMW Python Smart IDE — Developer & Architecture Guide

**Department of Computer Science and Engineering**  
**Gouthami Institute of Technology for Women (Autonomous), Proddatur**

---

## 1. Architecture Overview

GITAMW Python Smart IDE follows a modular client-server architecture running entirely on local loopback (`127.0.0.1`):

- **Backend Controller**: `app/main.py` built on FastAPI & Uvicorn.
- **Execution Subprocess Engine**: `app/execution_engine.py` captures stdout, stderr, execution duration, and RSS memory consumption using `psutil`.
- **Smart Error Explainer**: `app/smart_error_explainer.py` uses pattern matching on Python tracebacks to construct student-friendly tips.
- **Local Storage Engine**: `app/storage_manager.py` reads and writes `data/students.json`, `data/history.json`, and `data/settings.json`.
- **Workspace File System**: `app/file_manager.py` manages scripts in `saved_programs/` and `sample_programs/`.

---

## 2. Extending Smart Error Rules

To add explanations for new exception types, edit `app/smart_error_explainer.py`:

```python
elif "recursionerror" in error_type.lower():
    return {
        "category": "Recursion Depth Error",
        "explanation": "Your recursive function called itself too many times without hitting a base case.",
        "suggestion": "Check the base condition (if statement) in your recursive function to ensure it stops."
    }
```

---

## 3. Adding New Sample Lab Programs

To add a new pre-loaded lab experiment for students:
1. Place a `.py` file inside `sample_programs/` (e.g. `12_neural_networks.py`).
2. Re-launch the application. It will automatically populate under the **CSE Lab Code** sidebar tab.

---
