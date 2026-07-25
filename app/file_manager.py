"""
GITAMW Python Smart IDE — File Manager
=======================================
Gouthami Institute of Technology and Management for Women (Autonomous)
Department of Computer Science & Engineering

FIXES:
  Issue 1 — Per-user file isolation:
    Files are now stored under saved_programs/<user_id>/ where user_id is
    derived from the student's roll number (URL-safe, lowercase).
    All CRUD operations require a user_id parameter so one user can never
    read, overwrite, or delete another user's files — even by guessing a name.

    Path traversal protection: os.path.basename() is applied to every filename,
    and the resolved absolute path is verified to be inside the user's own
    directory before any I/O is performed.

  Issue 2 — PDF report contains full code + actual console output:
    The generate_html_report() helper (retained for compatibility) already had
    stdout/stderr.  The real PDF export logic is in main.py and now stores
    the full code and output in history (see storage_manager.py fix).
"""

import os
import re
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime


def _safe_user_id(roll_number: str) -> str:
    """
    Convert a roll number to a safe filesystem directory name.
    Keeps only alphanumeric chars and underscores; lowercases everything.
    e.g. '212M1A0501' → '212m1a0501'
    """
    safe = re.sub(r'[^a-zA-Z0-9_]', '_', roll_number.strip())
    return safe.lower() or "guest"


class FileManager:
    """
    Manages workspace user files, saved scripts, sample lab programs,
    and report generation exports.

    Per-user isolation:
        saved_programs/<user_id>/filename.py
        (one directory per student, keyed by sanitised roll number)
    """

    def __init__(self, saved_dir: str = "saved_programs", sample_dir: str = "sample_programs"):
        self.saved_root = os.path.abspath(saved_dir)   # root; sub-dirs created per user
        self.sample_dir = os.path.abspath(sample_dir)
        os.makedirs(self.saved_root, exist_ok=True)
        os.makedirs(self.sample_dir, exist_ok=True)
        self._init_samples()

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _user_dir(self, user_id: str) -> str:
        """
        Return (and create if needed) the per-user saved-programs directory.
        This is the ONLY place a user's files may be stored.
        """
        path = os.path.join(self.saved_root, _safe_user_id(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    def _safe_path(self, user_id: str, filename: str) -> str:
        """
        Build an absolute file path inside the user's directory and verify
        it does not escape that directory (path traversal protection).
        Raises ValueError if the resolved path is outside the user's dir.
        """
        user_dir = self._user_dir(user_id)
        # Strip any directory separators from the filename component
        safe_name = os.path.basename(filename)
        full_path = os.path.realpath(os.path.join(user_dir, safe_name))
        real_user_dir = os.path.realpath(user_dir)
        if not full_path.startswith(real_user_dir + os.sep) and full_path != real_user_dir:
            raise ValueError(f"Access denied: '{filename}' is outside user directory.")
        return full_path

    # ── Sample programs ───────────────────────────────────────────────────────

    def _init_samples(self):
        """Creates sample GITAMW lab programs if the sample directory is empty."""
        samples = {
            "01_hello_world.py": '''# GITAMW Python Smart IDE - Lab Program 01
# Program: Hello World & Student Greeting
# Department of Computer Science & Engineering

student_name = "GITAMW Student"
college = "Gouthami Institute of Technology for Women (Autonomous)"
city = "Proddatur"

print(f"Welcome to {college}, {city}!")
print(f"Happy Coding with Python Smart IDE, {student_name}!")
print("-" * 55)
''',
            "02_variables_and_types.py": '''# Lab Program 02: Python Data Types & Variables
roll_no = "212M1A0501"
branch = "CSE"
year = 3
cgpa = 8.95
is_enrolled = True

print(f"Roll Number : {roll_no}")
print(f"Branch      : {branch}")
print(f"Year        : {year}")
print(f"CGPA        : {cgpa} (Type: {type(cgpa).__name__})")
print(f"Active Status: {is_enrolled}")
''',
            "03_control_flow.py": '''# Lab Program 03: Control Flow (Loops & Conditionals)
print("=== Even / Odd Classifier (1 to 10) ===")

for num in range(1, 11):
    if num % 2 == 0:
        print(f"Number {num:2d} is EVEN")
    else:
        print(f"Number {num:2d} is ODD")

print("\\nGrade Evaluator Example:")
marks = 87
if marks >= 90:
    grade = "A+ (Outstanding)"
elif marks >= 80:
    grade = "A (Excellent)"
elif marks >= 70:
    grade = "B (Good)"
else:
    grade = "Pass"

print(f"Marks: {marks} -> Grade: {grade}")
''',
            "04_functions.py": '''# Lab Program 04: Python Functions & Recursion

def calculate_factorial(n: int) -> int:
    """Calculates factorial of n using recursion."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def is_prime(number: int) -> bool:
    """Checks if a number is prime."""
    if number <= 1:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True

print("Factorial of 5:", calculate_factorial(5))
print("Is 17 Prime?:", is_prime(17))
print("Is 24 Prime?:", is_prime(24))
''',
            "05_data_structures.py": '''# Lab Program 05: Lists, Tuples, Sets, and Dictionaries

# List Operations
students = ["Sravani", "Anusha", "Priya", "Divya"]
students.append("Lakshmi")
print("CSE Students List:", students)

# Dictionary Operations
student_info = {
    "name": "K. Sravani",
    "roll_no": "222M1A0512",
    "branch": "CSE",
    "skills": ["Python", "HTML", "C++"]
}
print("\\nStudent Profile Dictionary:")
for key, val in student_info.items():
    print(f"  {key.title()}: {val}")
''',
            "06_oop_concepts.py": '''# Lab Program 06: Object-Oriented Programming (OOP)

class Student:
    def __init__(self, name: str, roll_no: str, branch: str = "CSE"):
        self.name = name
        self.roll_no = roll_no
        self.branch = branch
        self.marks = {}

    def add_marks(self, subject: str, score: float):
        self.marks[subject] = score

    def calculate_average(self) -> float:
        if not self.marks:
            return 0.0
        return sum(self.marks.values()) / len(self.marks)

    def display(self):
        print(f"Student Name: {self.name} | Roll: {self.roll_no} | Branch: {self.branch}")
        print(f"Average Marks: {self.calculate_average():.2f}")

s1 = Student("A. Harshitha", "212M1A0505")
s1.add_marks("Python Programming", 92)
s1.add_marks("Data Structures", 88)
s1.add_marks("Database Systems", 95)
s1.display()
''',
            "07_file_handling.py": '''# Lab Program 07: Local File I/O Operations

file_path = "sample_output.txt"

with open(file_path, "w", encoding="utf-8") as f:
    f.write("Gouthami Institute of Technology for Women, Proddatur\\n")
    f.write("Department of Computer Science & Engineering\\n")
    f.write("Python Smart IDE Offline File Creation Test\\n")

print(f"Successfully wrote data to \'{file_path}\'.")

print("\\nReading file contents:")
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
''',
            "08_exception_handling.py": '''# Lab Program 08: Exception Handling Demonstration

print("=== Smart Exception Handling Test ===")

def safe_divide(a, b):
    try:
        result = a / b
        print(f"Division ({a} / {b}) = {result:.2f}")
    except ZeroDivisionError:
        print(f"[Caught Exception]: Cannot divide {a} by zero!")
    except TypeError:
        print(f"[Caught Exception]: Invalid input types provided.")
    finally:
        print("Execution of safe_divide block complete.\\n")

safe_divide(100, 5)
safe_divide(50, 0)
''',
            "09_numpy_basics.py": '''# Lab Program 09: NumPy Array Computations
try:
    import numpy as np
    arr1 = np.array([10, 20, 30, 40, 50])
    arr2 = np.array([[1, 2, 3], [4, 5, 6]])
    print("1D Array:", arr1)
    print("Array Mean:", np.mean(arr1))
    print("2D Matrix Transpose:\\n", arr2.T)
except ImportError:
    print("NumPy not installed. Use Package Manager tab to install it.")
''',
            "10_matplotlib_charts.py": '''# Lab Program 10: Matplotlib Data Visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 10, 100)
    plt.figure(figsize=(7, 4))
    plt.plot(x, np.sin(x), label="Sine", color="#1e3a8a", linewidth=2)
    plt.plot(x, np.cos(x), label="Cosine", color="#f97316", linewidth=2, linestyle="--")
    plt.title("GITAMW CSE - Mathematical Function Plot")
    plt.legend()
    plt.show()
    print("Chart rendered successfully!")
except ImportError:
    print("Matplotlib not installed. Install via Package Manager.")
''',
        }

        for filename, code in samples.items():
            filepath = os.path.join(self.sample_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)

    # ── File CRUD (all user-scoped) ────────────────────────────────────────────

    def list_files(self, user_id: str = "guest") -> Dict[str, List[Dict[str, Any]]]:
        """
        Lists ONLY the files belonging to ``user_id``.
        Sample lab programs are shared and visible to all users.
        """
        user_dir = self._user_dir(user_id)
        saved_files = []
        for filename in sorted(os.listdir(user_dir)):
            path = os.path.join(user_dir, filename)
            if os.path.isfile(path):
                stat = os.stat(path)
                saved_files.append({
                    "name":       filename,
                    "size_bytes": stat.st_size,
                    "modified":   datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_sample":  False,
                })

        sample_files = []
        for filename in sorted(os.listdir(self.sample_dir)):
            path = os.path.join(self.sample_dir, filename)
            if os.path.isfile(path):
                stat = os.stat(path)
                sample_files.append({
                    "name":       filename,
                    "size_bytes": stat.st_size,
                    "modified":   datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_sample":  True,
                })

        return {"saved": saved_files, "samples": sample_files}

    def read_file(self, filename: str, is_sample: bool = False,
                  user_id: str = "guest") -> Dict[str, Any]:
        """
        Read a file.  For saved files the user_id scope is enforced;
        for sample files it is ignored (samples are read-only shared).
        """
        if is_sample:
            path = os.path.join(self.sample_dir, os.path.basename(filename))
        else:
            path = self._safe_path(user_id, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{filename}' not found.")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "filename": os.path.basename(path),
            "content":  content,
            "is_sample": is_sample,
        }

    def save_file(self, filename: str, content: str,
                  user_id: str = "guest") -> Dict[str, Any]:
        """
        Save (create/overwrite) a file in the user's private directory.
        Enforces .py extension and path traversal protection.
        """
        if not (filename.endswith(".py") or filename.endswith(".txt")):
            filename += ".py"
        path = self._safe_path(user_id, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "filename": os.path.basename(path),
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def delete_file(self, filename: str, user_id: str = "guest") -> bool:
        """Delete a file only if it belongs to ``user_id``."""
        try:
            path = self._safe_path(user_id, filename)
        except ValueError:
            return False
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def duplicate_file(self, filename: str, user_id: str = "guest") -> Dict[str, Any]:
        """Duplicate a file within the user's own directory."""
        src = self._safe_path(user_id, filename)
        if not os.path.exists(src):
            raise FileNotFoundError(f"File '{filename}' not found.")
        base, ext = os.path.splitext(os.path.basename(filename))
        new_name = f"{base}_copy{ext}"
        dst = self._safe_path(user_id, new_name)
        shutil.copyfile(src, dst)
        return {"new_filename": new_name}

    # ── HTML report helper (kept for backwards compatibility) ─────────────────

    def generate_html_report(
        self,
        student_info: Dict[str, Any],
        program_name: str,
        code: str,
        result: Dict[str, Any],
    ) -> str:
        """Generates a standalone HTML execution report (single program)."""
        timestamp    = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        status_color = "#16a34a" if result.get("status") == "Success" else "#dc2626"

        def _esc(s: str) -> str:
            return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        stdout_html = _esc(result.get("stdout") or "No output generated.")
        stderr_html = _esc(result.get("stderr") or "")
        code_html   = _esc(code)

        smart_err = result.get("smart_error", {})
        err_box   = ""
        if smart_err and smart_err.get("has_error"):
            err_box = f"""
            <div style="background:#fef2f2;border:1px solid #fca5a5;padding:15px;border-radius:8px;margin-top:15px;">
                <h4 style="color:#991b1b;margin-top:0;">Smart Error Analysis: {smart_err.get('error_type')}</h4>
                <p><strong>Explanation:</strong> {smart_err.get('explanation')}</p>
                <p><strong>Suggestion:</strong> {smart_err.get('suggestion')}</p>
            </div>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Execution Report - {program_name}</title>
  <style>
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;color:#1e293b;padding:30px;}}
    .card{{background:white;padding:30px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,.05);max-width:900px;margin:0 auto;}}
    .header{{text-align:center;border-bottom:2px solid #1e3a8a;padding-bottom:15px;margin-bottom:20px;}}
    .header h2{{color:#1e3a8a;margin:0;font-size:24px;}}
    .meta-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;background:#f1f5f9;padding:15px;border-radius:8px;font-size:14px;}}
    pre{{background:#0f172a;color:#e2e8f0;padding:15px;border-radius:8px;overflow-x:auto;font-family:'Consolas',monospace;font-size:13px;}}
    .badge{{background:{status_color};color:white;padding:4px 10px;border-radius:20px;font-weight:bold;font-size:12px;display:inline-block;}}
    .footer{{text-align:center;margin-top:30px;font-size:12px;color:#64748b;border-top:1px solid #e2e8f0;padding-top:15px;}}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2>Gouthami Institute of Technology for Women (Autonomous)</h2>
      <h3>Department of Computer Science and Engineering — Python Smart IDE</h3>
    </div>
    <h3 style="color:#1e3a8a;">Program Execution Report: {program_name}</h3>
    <div class="meta-grid">
      <div><strong>Student Name:</strong> {student_info.get('name','N/A')}</div>
      <div><strong>Roll Number:</strong> {student_info.get('roll_number','N/A')}</div>
      <div><strong>Branch &amp; Year:</strong> {student_info.get('branch','CSE')} - {student_info.get('year','N/A')} Yr / Sem {student_info.get('semester','N/A')} ({student_info.get('section','A')})</div>
      <div><strong>Date &amp; Time:</strong> {timestamp}</div>
      <div><strong>Status:</strong> <span class="badge">{result.get('status','Completed')}</span></div>
      <div><strong>Runtime &amp; Memory:</strong> {result.get('duration_seconds',0)}s | {result.get('memory_mb',0)} MB</div>
    </div>
    <h4>Source Code:</h4>
    <pre>{code_html}</pre>
    <h4>Program Output:</h4>
    <pre>{stdout_html}</pre>
    {f"<h4>Errors:</h4><pre style='background:#450a0a;color:#fca5a5;'>{stderr_html}</pre>" if stderr_html else ""}
    {err_box}
    <div class="footer">Designed &amp; Developed by Department of CSE | GITAMW Proddatur</div>
  </div>
</body>
</html>"""
