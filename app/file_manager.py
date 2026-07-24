import os
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime

class FileManager:
    """
    Manages workspace user files, saved scripts, sample lab programs,
    and report generation exports.
    """
    def __init__(self, saved_dir: str = "saved_programs", sample_dir: str = "sample_programs"):
        self.saved_dir = os.path.abspath(saved_dir)
        self.sample_dir = os.path.abspath(sample_dir)
        os.makedirs(self.saved_dir, exist_ok=True)
        os.makedirs(self.sample_dir, exist_ok=True)
        self._init_samples()

    def _init_samples(self):
        """Creates sample GITAMW lab programs if empty."""
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

print("\nGrade Evaluator Example:")
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
print("\nStudent Profile Dictionary:")
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

# Instantiate Student Object
s1 = Student("A. Harshitha", "212M1A0505")
s1.add_marks("Python Programming", 92)
s1.add_marks("Data Structures", 88)
s1.add_marks("Database Systems", 95)
s1.display()
''',
            "07_file_handling.py": '''# Lab Program 07: Local File I/O Operations

file_path = "sample_output.txt"

# Write to local file
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Gouthami Institute of Technology for Women, Proddatur\\n")
    f.write("Department of Computer Science & Engineering\\n")
    f.write("Python Smart IDE Offline File Creation Test\\n")

print(f"Successfully wrote data to '{file_path}'.")

# Read from local file
print("\nReading file contents:")
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
    except ZeroDivisionError as e:
        print(f"[Caught Exception]: Cannot divide {a} by zero!")
    except TypeError as e:
        print(f"[Caught Exception]: Invalid input types provided.")
    finally:
        print("Execution of safe_divide block complete.\\n")

safe_divide(100, 5)
safe_divide(50, 0)
''',
            "09_numpy_basics.py": '''# Lab Program 09: NumPy Array Computations
try:
    import numpy as np
    print("NumPy Version:", np.__version__)

    # Create 1D and 2D arrays
    arr1 = np.array([10, 20, 30, 40, 50])
    arr2 = np.array([[1, 2, 3], [4, 5, 6]])

    print("1D Array:", arr1)
    print("Array Mean:", np.mean(arr1))
    print("Array Sum:", np.sum(arr1))
    print("\n2D Matrix Shape:", arr2.shape)
    print("2D Matrix Transpose:\\n", arr2.T)
except ImportError:
    print("NumPy is not installed. Please use the Package Manager tab to install NumPy.")
''',
            "10_pandas_dataframe.py": '''# Lab Program 10: Pandas DataFrame Operations
try:
    import pandas as pd

    data = {
        "Roll No": ["212M1A0501", "212M1A0502", "212M1A0503", "212M1A0504"],
        "Name": ["K. Sravani", "M. Anusha", "P. Divya", "T. Swapna"],
        "Python Marks": [95, 88, 92, 90],
        "Attendance %": [98.5, 92.0, 96.0, 94.5]
    }

    df = pd.DataFrame(data)
    print("=== GITAMW CSE Student Performance Table ===")
    print(df.to_string(index=False))

    print("\nAverage Python Marks:", df["Python Marks"].mean())
except ImportError:
    print("Pandas is not installed. Please install Pandas using the Package Manager.")
''',
            "11_matplotlib_charts.py": '''# Lab Program 11: Matplotlib Data Visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np

    # Generate sample data
    x = np.linspace(0, 10, 100)
    y_sine = np.sin(x)
    y_cosine = np.cos(x)

    plt.figure(figsize=(7, 4))
    plt.plot(x, y_sine, label="Sine Wave", color="#1e3a8a", linewidth=2)
    plt.plot(x, y_cosine, label="Cosine Wave", color="#f97316", linewidth=2, linestyle="--")

    plt.title("GITAMW CSE - Mathematical Function Plot", fontsize=12, fontweight="bold")
    plt.xlabel("X Value", fontsize=10)
    plt.ylabel("Y Value", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    # In GITAMW Python Smart IDE, plots rendered via plt.show()
    # are automatically displayed directly in the IDE Output Window!
    plt.show()
    print("Chart plotted and rendered successfully!")
except ImportError:
    print("Matplotlib is not installed. Install Matplotlib via the Package Manager tab.")
'''
        }

        for filename, code in samples.items():
            filepath = os.path.join(self.sample_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)

    def list_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lists user saved files and sample lab programs."""
        saved_files = []
        for filename in sorted(os.listdir(self.saved_dir)):
            path = os.path.join(self.saved_dir, filename)
            if os.path.isfile(path):
                stat = os.stat(path)
                saved_files.append({
                    "name": filename,
                    "path": path,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_sample": False
                })

        sample_files = []
        for filename in sorted(os.listdir(self.sample_dir)):
            path = os.path.join(self.sample_dir, filename)
            if os.path.isfile(path):
                stat = os.stat(path)
                sample_files.append({
                    "name": filename,
                    "path": path,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_sample": True
                })

        return {
            "saved": saved_files,
            "samples": sample_files
        }

    def read_file(self, filename: str, is_sample: bool = False) -> Dict[str, Any]:
        folder = self.sample_dir if is_sample else self.saved_dir
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{filename}' not found.")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "filename": filename,
            "content": content,
            "is_sample": is_sample,
            "path": path
        }

    def save_file(self, filename: str, content: str) -> Dict[str, Any]:
        # Ensure .py extension if none given
        if not (filename.endswith(".py") or filename.endswith(".txt")):
            filename += ".py"
        # Sanitize filename
        filename = os.path.basename(filename)
        path = os.path.join(self.saved_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "filename": filename,
            "path": path,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def delete_file(self, filename: str) -> bool:
        path = os.path.join(self.saved_dir, os.path.basename(filename))
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def duplicate_file(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.saved_dir, os.path.basename(filename))
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{filename}' not found.")
        
        base, ext = os.path.splitext(filename)
        new_filename = f"{base}_copy{ext}"
        new_path = os.path.join(self.saved_dir, new_filename)
        shutil.copyfile(path, new_path)
        return {"new_filename": new_filename, "path": new_path}

    def generate_html_report(self, student_info: Dict[str, Any], program_name: str, code: str, result: Dict[str, Any]) -> str:
        """Generates standalone HTML execution report."""
        timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        status_color = "#16a34a" if result.get("status") == "Success" else "#dc2626"
        
        stdout_html = (result.get("stdout") or "No output generated.").replace("<", "&lt;").replace(">", "&gt;")
        stderr_html = (result.get("stderr") or "").replace("<", "&lt;").replace(">", "&gt;")
        code_html = code.replace("<", "&lt;").replace(">", "&gt;")
        
        smart_err = result.get("smart_error", {})
        err_box = ""
        if smart_err and smart_err.get("has_error"):
            err_box = f"""
            <div style="background:#fef2f2; border:1px solid #fca5a5; padding:15px; border-radius:8px; margin-top:15px;">
                <h4 style="color:#991b1b; margin-top:0;">💡 Smart Error Analysis: {smart_err.get('error_type')}</h4>
                <p><strong>Explanation:</strong> {smart_err.get('explanation')}</p>
                <p><strong>Suggestion:</strong> {smart_err.get('suggestion')}</p>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Execution Report - {program_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #1e293b; padding: 30px; }}
        .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); max-width: 900px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 20px; }}
        .header h2 {{ color: #1e3a8a; margin: 0; font-size: 24px; }}
        .header h3 {{ color: #475569; margin: 5px 0 0 0; font-size: 16px; font-weight: normal; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #f1f5f9; padding: 15px; border-radius: 8px; font-size: 14px; }}
        pre {{ background: #0f172a; color: #e2e8f0; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 13px; }}
        .badge {{ background: {status_color}; color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 12px; display: inline-block; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
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
            <div><strong>Student Name:</strong> {student_info.get('name', 'N/A')}</div>
            <div><strong>Roll Number:</strong> {student_info.get('roll_number', 'N/A')}</div>
            <div><strong>Branch & Year:</strong> {student_info.get('branch', 'CSE')} - {student_info.get('year', 'N/A')} Yr / Sem {student_info.get('semester', 'N/A')} ({student_info.get('section', 'A')})</div>
            <div><strong>Date & Time:</strong> {timestamp}</div>
            <div><strong>Execution Status:</strong> <span class="badge">{result.get('status', 'Completed')}</span></div>
            <div><strong>Runtime & Memory:</strong> {result.get('duration_seconds', 0)}s | {result.get('memory_mb', 0)} MB</div>
        </div>

        <h4>Source Code:</h4>
        <pre>{code_html}</pre>

        <h4>Program Output:</h4>
        <pre>{stdout_html}</pre>

        {f"<h4>Errors:</h4><pre style='background:#450a0a; color:#fca5a5;'>{stderr_html}</pre>" if stderr_html else ""}
        {err_box}

        <div class="footer">
            Designed & Developed by Department of Computer Science and Engineering | GITAMW Proddatur
        </div>
    </div>
</body>
</html>"""
        return html_content
