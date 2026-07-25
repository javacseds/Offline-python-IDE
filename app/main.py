import os
import sys
import platform
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.storage_manager import StorageManager
from app.execution_engine import ExecutionEngine
from app.package_manager import PackageManager
from app.file_manager import FileManager

# Initialize FastAPI App
app = FastAPI(
    title="GITAMW Python Smart IDE",
    description="Offline Python IDE for Gouthami Institute of Technology and Management for Women (Autonomous), Proddatur",
    version="1.0.0"
)

# ── Path resolution: works in both normal and PyInstaller onefile/onedir mode ──
# In frozen (onefile) mode, sys._MEIPASS is the temp extraction directory.
# In frozen (onedir) mode, sys._MEIPASS is the _internal directory.
# In dev mode, resolve from this file's real location.
if getattr(sys, "frozen", False):
    # Running as a PyInstaller bundle
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# App-level data lives next to the .exe (persists across runs), not in _MEIPASS
if getattr(sys, "frozen", False):
    DATA_ROOT = os.path.dirname(sys.executable)
else:
    DATA_ROOT = BASE_DIR

STATIC_DIR    = os.path.join(BASE_DIR,  "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR,  "app", "templates")
DATA_DIR      = os.path.join(DATA_ROOT, "data")
SAVED_DIR     = os.path.join(DATA_ROOT, "saved_programs")
SAMPLE_DIR    = os.path.join(BASE_DIR,  "sample_programs")

# Mount Static Files & Templates
os.makedirs(STATIC_DIR,    exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DATA_DIR,      exist_ok=True)
os.makedirs(SAVED_DIR,     exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Initialize Core Services
storage = StorageManager(data_dir=DATA_DIR)
file_mgr = FileManager(
    saved_dir=SAVED_DIR,
    sample_dir=SAMPLE_DIR
)

# Active Session In-Memory Cache
current_student_session: Dict[str, Any] = {}

# --- Pydantic Data Models ---
class StudentLoginModel(BaseModel):
    name: str = Field(..., min_length=2, description="Student Name")
    roll_number: str = Field(..., min_length=5, description="Roll Number")
    branch: str = Field(default="CSE")
    year: str = Field(..., description="Year (e.g. 1, 2, 3, 4)")
    semester: str = Field(..., description="Semester (e.g. 1, 2)")
    section: str = Field(default="A")
    email: Optional[str] = ""
    mobile: Optional[str] = ""
    agreed_policy: bool = Field(..., description="Must agree to academic integrity policy")

class ExecuteCodeModel(BaseModel):
    code: str = Field(..., description="Python source code")
    program_name: Optional[str] = "untitled.py"
    stdin_inputs: Optional[list] = Field(default=None, description="List of input() values to feed as stdin")

class SaveFileModel(BaseModel):
    filename: str
    content: str

class PipInstallModel(BaseModel):
    package_name: str

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def serve_ide_index(request: Request):
    """Renders the single page application interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "python_version": platform.python_version(),
            "os_info": platform.platform()
        }
    )

@app.get("/api/system/info")
async def get_system_info():
    """Returns local system metadata."""
    return {
        "college": "Gowthami Institute of Technology and Management for Women (Autonomous)",
        "location": "Proddatur",
        "app_name": "GITAMW Python Smart IDE",
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- Student Login & Auth ---
@app.post("/api/auth/login")
async def student_login(data: StudentLoginModel):
    """Validates student login data and stores record locally in JSON."""
    if not data.agreed_policy:
        raise HTTPException(status_code=400, detail="❌ You must agree to the Academic Integrity Policy to proceed.")

    # Validation Checks
    name_clean = data.name.strip()
    roll_clean = data.roll_number.strip().upper()
    
    if not name_clean:
        raise HTTPException(status_code=400, detail="❌ Student Name cannot be empty.")
    if not roll_clean or len(roll_clean) < 4:
        raise HTTPException(status_code=400, detail="❌ Enter a valid Roll Number.")
    if data.year not in ["1", "2", "3", "4", "I", "II", "III", "IV"]:
        raise HTTPException(status_code=400, detail="❌ Invalid Year selection. Must be 1, 2, 3, or 4.")
    if data.semester not in ["1", "2", "I", "II"]:
        raise HTTPException(status_code=400, detail="❌ Invalid Semester selection. Must be 1 or 2.")

    # Save to local JSON storage
    saved_profile = storage.save_student(data.model_dump())
    
    global current_student_session
    current_student_session = saved_profile
    
    return {
        "success": True,
        "message": f"Welcome, {saved_profile['name']}!",
        "student": saved_profile
    }

@app.get("/api/auth/current")
async def get_current_student():
    """Returns currently logged in student session."""
    return {"student": current_student_session}

# --- Input Detection ---
@app.post("/api/execute/detect-inputs")
async def detect_inputs(payload: ExecuteCodeModel):
    """Scans code for input() calls and returns count + prompt labels for the frontend dialog."""
    # Delegate to the engine's detection method (single source of truth)
    prompts = ExecutionEngine.detect_input_calls(payload.code)

    # Give generic labels to any blank prompts (e.g. bare input() with no string)
    labeled = []
    for i, label in enumerate(prompts):
        labeled.append(label if label else f"Input {i + 1}")

    return {
        "input_count":  len(labeled),
        "prompts":      labeled,
        "needs_input":  len(labeled) > 0,
    }

# --- Code Execution ---
@app.post("/api/execute")
async def execute_code(payload: ExecuteCodeModel):
    """Executes Python code locally and returns stdout, telemetry, and smart error analysis."""
    if not payload.code.strip():
        return {
            "status": "Success",
            "stdout": "",
            "stderr": "",
            "duration_seconds": 0.0,
            "memory_mb": 0.0,
            "plots": [],
            "smart_error": {"has_error": False}
        }

    # Run in subprocess (with optional pre-collected stdin values)
    result = ExecutionEngine.execute(payload.code, stdin_inputs=payload.stdin_inputs)

    # Log to execution history JSON
    roll = current_student_session.get("roll_number", "GUEST")
    name = current_student_session.get("name", "Guest Student")
    
    storage.log_execution(
        roll_number=roll,
        student_name=name,
        program_name=payload.program_name or "untitled.py",
        code=payload.code,
        status=result["status"],
        duration=result["duration_seconds"],
        memory_mb=result["memory_mb"],
        output=result["stdout"],
        error=result["stderr"]
    )

    return result

# --- File Management (per-user isolated) ---
def _current_user_id() -> str:
    """Return the current student's roll number as user-dir key, or 'guest'."""
    roll = current_student_session.get("roll_number", "").strip().upper()
    return roll if roll else "guest"

@app.get("/api/files/list")
async def list_workspace_files():
    """Lists ONLY the current user's saved programs + shared sample programs."""
    return file_mgr.list_files(user_id=_current_user_id())

@app.get("/api/files/read")
async def read_file(name: str, sample: bool = False):
    """Reads a file — user-scoped for saved files, shared for samples."""
    try:
        return file_mgr.read_file(name, is_sample=sample, user_id=_current_user_id())
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/files/save")
async def save_file(payload: SaveFileModel):
    """Saves user code under the current user's private directory."""
    if not payload.filename.strip():
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")
    try:
        saved = file_mgr.save_file(payload.filename, payload.content, user_id=_current_user_id())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "file": saved}

@app.delete("/api/files/delete")
async def delete_file(filename: str):
    """Deletes a file — only allowed if it belongs to the current user."""
    success = file_mgr.delete_file(filename, user_id=_current_user_id())
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied.")
    return {"success": True, "message": f"Deleted {filename}"}

@app.post("/api/files/duplicate")
async def duplicate_file(filename: str = Body(..., embed=True)):
    """Duplicates a file within the current user's own directory."""
    try:
        res = file_mgr.duplicate_file(filename, user_id=_current_user_id())
        return {"success": True, "duplicate": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Package Management ---
@app.get("/api/packages/list")
async def list_packages():
    """Returns preinstalled package status."""
    return {"packages": PackageManager.get_installed_packages()}

@app.post("/api/packages/install")
async def install_package(payload: PipInstallModel):
    """Runs pip install locally."""
    res = PackageManager.install_package(payload.package_name)
    return res

# --- Execution History & Settings ---
@app.get("/api/history")
async def get_history():
    """Returns local execution history log."""
    roll = current_student_session.get("roll_number")
    return {"history": storage.get_history(roll_number=roll)}

@app.delete("/api/history/clear")
async def clear_history():
    """Clears history for current student."""
    roll = current_student_session.get("roll_number")
    storage.clear_history(roll_number=roll)
    return {"success": True, "message": "Execution history cleared."}

@app.get("/api/settings")
async def get_settings():
    """Returns IDE editor preferences."""
    return storage.get_settings()

@app.post("/api/settings/update")
async def update_settings(settings: Dict[str, Any] = Body(...)):
    """Updates IDE preferences."""
    updated = storage.update_settings(settings)
    return {"success": True, "settings": updated}

# --- Export Report (PDF with full code + console output) ---
@app.post("/api/export/report")
async def export_report(payload: Dict[str, Any] = Body(...)):
    """Generates PDF report with full source code AND console output, scoped by user and date option."""
    roll = current_student_session.get("roll_number")
    if not roll:
        raise HTTPException(status_code=401, detail="Please log in to export your report.")

    export_filter = payload.get("filter", "today").lower()  # "today" or "all"
    current_code = payload.get("code", "")
    current_program = payload.get("program_name", "untitled.py")

    # Fetch execution history for current logged-in student ONLY
    history_records = storage.get_history(roll_number=roll)

    # Helper function to detect sample/boilerplate/untouched starter code
    def is_boilerplate(c: str) -> bool:
        if not c or not c.strip():
            return True
        st = c.strip()
        if "welcome_student(" in st:
            return True
        if st.startswith("# GITAMW Python Smart IDE"):
            return True
        if st.startswith("# Lab Program 0") or st.startswith("# Lab Program 1") or st.startswith("# Lab Program"):
            return True
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Filter records based on user scope, date option, and boilerplate exclusion
    records = []
    for rec in (history_records or []):
        rec_time = rec.get("timestamp", "")
        code_text = rec.get("full_code") or rec.get("code_snippet") or ""

        # Scope Option A: Today's Programs
        if export_filter == "today" and not rec_time.startswith(today_str):
            continue

        # Exclude boilerplate / default template code
        if is_boilerplate(code_text):
            continue

        records.append(rec)

    # Fallback: Check if current active editor code is non-boilerplate
    if not records and current_code and not is_boilerplate(current_code):
        # Current open code is student-written
        # If "today" filter is set, allow it since active session is today
        records.append({
            "program_name": current_program,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Not Run",
            "full_code": current_code,
            "full_output": "",
            "full_error": ""
        })

    # Empty State Check: If no matching programs found, return friendly error
    if not records:
        if export_filter == "today":
            raise HTTPException(status_code=404, detail="No programs found for today.")
        else:
            raise HTTPException(status_code=404, detail="No user programs found in history.")

    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, Preformatted, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontSize=14, leading=17, textColor=colors.HexColor("#1e3a8a"),
        alignment=1, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontSize=10, leading=13, textColor=colors.HexColor("#3b82f6"),
        alignment=1, spaceAfter=8
    )
    heading_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading3'],
        fontSize=11, leading=14, textColor=colors.HexColor("#1e293b"),
        spaceBefore=10, spaceAfter=5
    )
    label_style = ParagraphStyle(
        'Label', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor("#64748b"),
        spaceBefore=8, spaceAfter=2
    )
    code_style = ParagraphStyle(
        'CodeStyle', fontName='Courier', fontSize=8,
        leading=10, textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderPadding=6, spaceAfter=4
    )
    output_style = ParagraphStyle(
        'OutputStyle', fontName='Courier', fontSize=8,
        leading=10, textColor=colors.HexColor("#064e3b"),
        backColor=colors.HexColor("#f0fdf4"),
        borderPadding=6, spaceAfter=4
    )
    error_style = ParagraphStyle(
        'ErrorStyle', fontName='Courier', fontSize=8,
        leading=10, textColor=colors.HexColor("#7f1d1d"),
        backColor=colors.HexColor("#fef2f2"),
        borderPadding=6, spaceAfter=4
    )

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    scope_title = "Today's Programs" if export_filter == "today" else "All Programs — Full History"
    story.append(Paragraph("Gouthami Institute of Technology and Management for Women (Autonomous)", title_style))
    story.append(Paragraph(f"Python Smart IDE — Student Lab Execution Report ({scope_title})", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e3a8a")))
    story.append(Spacer(1, 8))

    # ── Student details ───────────────────────────────────────────────────────
    name     = current_student_session.get("name", "Student")
    roll_num = current_student_session.get("roll_number", "N/A")
    branch   = current_student_session.get("branch", "CSE")
    year     = current_student_session.get("year", "1")
    sem      = current_student_session.get("semester", "1")
    sec      = current_student_session.get("section", "A")

    info_data = [
        [Paragraph(f"<b>Student Name:</b> {name}", styles['Normal']),
         Paragraph(f"<b>Roll Number:</b> {roll_num}", styles['Normal'])],
        [Paragraph(f"<b>Branch &amp; Class:</b> {branch} Yr-{year}/Sem-{sem} Sec-{sec}", styles['Normal']),
         Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])],
    ]
    t = Table(info_data, colWidths=[270, 270])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX',        (0, 0), (-1, -1), 1,   colors.HexColor("#cbd5e1")),
        ('INNERGRID',  (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING',    (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"<b>Executed Programs Log ({len(records)} Entry/Entries — {scope_title})</b>", heading_style))
    story.append(Spacer(1, 4))


    # ── One section per program ───────────────────────────────────────────────
    for idx, rec in enumerate(records, start=1):
        p_name     = rec.get("program_name", f"program_{idx}.py")
        ts         = rec.get("timestamp", "")
        st         = rec.get("status", "Executed")
        duration   = rec.get("duration_seconds", "")
        memory     = rec.get("memory_mb", "")

        # Use full_code if available, fall back to code_snippet for old records
        full_code  = rec.get("full_code") or rec.get("code_snippet") or "# No code recorded"
        # Use full_output / full_error if available (new records); fall back to preview
        full_out   = rec.get("full_output") or rec.get("output_preview") or ""
        full_err   = rec.get("full_error")  or ""

        status_color = "green" if st == "Success" else ("grey" if st == "Not Run" else "red")
        dur_text     = f" | Runtime: {duration}s | Memory: {memory} MB" if duration else ""
        meta_line    = (f"<b>Program #{idx}: {p_name}</b> &nbsp;|&nbsp; "
                        f"Time: {ts}{dur_text} &nbsp;|&nbsp; "
                        f"Status: <font color='{status_color}'><b>{st}</b></font>")
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
        story.append(Spacer(1, 4))
        story.append(Paragraph(meta_line, styles['Normal']))
        story.append(Spacer(1, 3))

        # ── Source Code section ──────────────────────────────────────────────
        story.append(Paragraph("Source Code:", label_style))
        story.append(Preformatted(full_code, code_style))

        # ── Console Output section ───────────────────────────────────────────
        story.append(Paragraph("Console Output:", label_style))
        if full_out.strip():
            story.append(Preformatted(full_out, output_style))
        elif st == "Not Run":
            story.append(Paragraph(
                "<i>No output available — please run the code before exporting.</i>",
                styles['Normal']
            ))
        else:
            story.append(Paragraph("<i>(No output produced)</i>", styles['Normal']))

        # ── Errors section (only if present) ────────────────────────────────
        if full_err.strip():
            story.append(Paragraph("Errors / Stderr:", label_style))
            story.append(Preformatted(full_err, error_style))

        story.append(Spacer(1, 8))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8")))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Designed &amp; Developed by Department of Computer Science &amp; Engineering | "
        "GITAMW-Python-IDE-Design and Developed by Dept. of CSE",
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=8, textColor=colors.HexColor("#64748b"), alignment=1)
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()

    filename = f"GITAMW_Lab_Report_{roll_num if roll_num != 'N/A' else 'Session'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

