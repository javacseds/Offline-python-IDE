import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class StorageManager:
    """
    Manages local JSON data storage for Student Profiles, Execution History, and IDE Settings.
    Ensures 100% offline, zero-database operations.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.students_file = os.path.join(self.data_dir, "students.json")
        self.history_file = os.path.join(self.data_dir, "history.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        self._init_storage()

    def _init_storage(self):
        """Initializes empty JSON files if they do not exist."""
        if not os.path.exists(self.students_file):
            self._write_json(self.students_file, [])
        if not os.path.exists(self.history_file):
            self._write_json(self.history_file, [])
        if not os.path.exists(self.settings_file):
            default_settings = {
                "theme": "dark",
                "fontSize": 14,
                "tabSize": 4,
                "autoSave": True,
                "wordWrap": "on",
                "minimap": False
            }
            self._write_json(self.settings_file, default_settings)

    def _read_json(self, filepath: str) -> Any:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return [] if "settings" not in filepath else {}

    def _write_json(self, filepath: str, data: Any):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # --- Student Profile Operations ---
    def save_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves or updates student login record locally."""
        students = self._read_json(self.students_file)
        roll_no = str(student_data.get("roll_number", "")).strip().upper()
        
        record = {
            "name": str(student_data.get("name", "")).strip(),
            "roll_number": roll_no,
            "branch": str(student_data.get("branch", "CSE")).strip(),
            "year": str(student_data.get("year", "")).strip(),
            "semester": str(student_data.get("semester", "")).strip(),
            "section": str(student_data.get("section", "")).strip(),
            "email": str(student_data.get("email", "")).strip(),
            "mobile": str(student_data.get("mobile", "")).strip(),
            "last_login": datetime.now().isoformat()
        }
        
        # Update existing record or append new
        updated = False
        for idx, s in enumerate(students):
            if s.get("roll_number") == roll_no:
                students[idx] = record
                updated = True
                break
        if not updated:
            students.append(record)
            
        self._write_json(self.students_file, students)
        return record

    def get_student(self, roll_number: str) -> Optional[Dict[str, Any]]:
        """Finds student profile by roll number."""
        students = self._read_json(self.students_file)
        roll_no = roll_number.strip().upper()
        for s in students:
            if s.get("roll_number") == roll_no:
                return s
        return None

    # --- Execution History Operations ---
    def log_execution(self, roll_number: str, student_name: str, program_name: str,
                      code: str, status: str, duration: float, memory_mb: float,
                      output: str, error: str = ""):
        """
        Logs program execution entry into history.json.

        FIX (Issue 2): Stores the FULL source code and FULL stdout/stderr output
        so the PDF export can include complete content.  The legacy
        code_snippet / output_preview fields are kept (truncated) for display
        performance in the History tab; full_code and full_output are the
        authoritative fields used by PDF export.
        """
        history = self._read_json(self.history_file)
        entry = {
            "id":               len(history) + 1,
            "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "roll_number":      roll_number,
            "student_name":     student_name,
            "program_name":     program_name,
            # ── Display fields (truncated for UI performance) ──
            "code_snippet":     code[:200] + ("..." if len(code) > 200 else ""),
            "output_preview":   output[:300] if output else "",
            # ── Full fields used by PDF export ──────────────────
            "full_code":        code,
            "full_output":      output or "",
            "full_error":       error or "",
            # ── Telemetry ───────────────────────────────────────
            "status":           status,
            "duration_seconds": round(duration, 3),
            "memory_mb":        round(memory_mb, 2),
            "has_error":        bool(error),
        }
        history.insert(0, entry)   # Most recent first
        if len(history) > 500:
            history = history[:500]
        self._write_json(self.history_file, history)


    def get_history(self, roll_number: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns execution history filtered by student or all."""
        history = self._read_json(self.history_file)
        if roll_number:
            roll_no = roll_number.strip().upper()
            return [h for h in history if h.get("roll_number") == roll_no]
        return history

    def clear_history(self, roll_number: Optional[str] = None):
        """Clears execution history."""
        if roll_number:
            history = self._read_json(self.history_file)
            roll_no = roll_number.strip().upper()
            history = [h for h in history if h.get("roll_number") != roll_no]
            self._write_json(self.history_file, history)
        else:
            self._write_json(self.history_file, [])

    # --- IDE Settings ---
    def get_settings(self) -> Dict[str, Any]:
        return self._read_json(self.settings_file)

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_settings()
        current.update(new_settings)
        self._write_json(self.settings_file, current)
        return current
