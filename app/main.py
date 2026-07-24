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
    description="Offline Python IDE for Gowthami Institute of Technology and Management for Women (Autonomous), Proddatur",
    version="1.0.0"
)

# Resolve Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Mount Static Files & Templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Initialize Core Services
storage = StorageManager(data_dir=os.path.join(BASE_DIR, "data"))
file_mgr = FileManager(
    saved_dir=os.path.join(BASE_DIR, "saved_programs"),
    sample_dir=os.path.join(BASE_DIR, "sample_programs")
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

    # Run in subprocess
    result = ExecutionEngine.execute(payload.code)

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

# --- File Management ---
@app.get("/api/files/list")
async def list_workspace_files():
    """Lists saved student programs and sample lab programs."""
    return file_mgr.list_files()

@app.get("/api/files/read")
async def read_file(name: str, sample: bool = False):
    """Reads content of a saved or sample Python file."""
    try:
        return file_mgr.read_file(name, is_sample=sample)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/files/save")
async def save_file(payload: SaveFileModel):
    """Saves user code to disk."""
    if not payload.filename.strip():
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")
    saved = file_mgr.save_file(payload.filename, payload.content)
    return {"success": True, "file": saved}

@app.delete("/api/files/delete")
async def delete_file(filename: str):
    """Deletes a saved user file."""
    success = file_mgr.delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found.")
    return {"success": True, "message": f"Deleted {filename}"}

@app.post("/api/files/duplicate")
async def duplicate_file(filename: str = Body(..., embed=True)):
    """Duplicates a saved file."""
    try:
        res = file_mgr.duplicate_file(filename)
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

# --- Export Report (PDF) ---
@app.post("/api/export/report")
async def export_report(payload: Dict[str, Any] = Body(...)):
    """Generates PDF report containing all programs executed by student after login."""
    roll = current_student_session.get("roll_number")
    history_records = storage.get_history(roll_number=roll)
    
    current_code = payload.get("code", "")
    current_program = payload.get("program_name", "untitled.py")
    
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1e3a8a"),
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#3b82f6"),
        alignment=1,
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderPadding=6,
        spaceAfter=6
    )

    story = []

    # Header
    story.append(Paragraph("Gowthami Institute of Technology and Management for Women (Autonomous)", title_style))
    story.append(Paragraph("Python Smart IDE — Cumulative Student Lab Execution Report", subtitle_style))
    story.append(Spacer(1, 4))

    # Student Details Table
    name = current_student_session.get("name", "Student")
    roll_num = current_student_session.get("roll_number", "N/A")
    branch = current_student_session.get("branch", "CSE")
    year = current_student_session.get("year", "1")
    sem = current_student_session.get("semester", "1")
    sec = current_student_session.get("section", "A")

    info_data = [
        [Paragraph(f"<b>Student Name:</b> {name}", styles['Normal']), Paragraph(f"<b>Roll Number:</b> {roll_num}", styles['Normal'])],
        [Paragraph(f"<b>Branch & Class:</b> {branch} Yr-{year}/Sem-{sem} ({sec})", styles['Normal']), Paragraph(f"<b>Generated Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])]
    ]
    t = Table(info_data, colWidths=[270, 270])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Compile programs
    records = list(history_records) if history_records else []
    if not records and current_code:
        records.append({
            "program_name": current_program,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active",
            "code_snippet": current_code
        })

    story.append(Paragraph(f"<b>Executed Programs Log ({len(records)} Entry/Entries)</b>", heading_style))
    story.append(Spacer(1, 4))

    for idx, rec in enumerate(records, start=1):
        p_name = rec.get("program_name", f"program_{idx}.py")
        ts = rec.get("timestamp", "")
        st = rec.get("status", "Executed")
        cd = rec.get("code", rec.get("code_snippet", "# No code recorded"))
        
        status_color = "green" if st == "Success" else "red"
        meta_line = f"<b>Program #{idx}: {p_name}</b> &nbsp;|&nbsp; Time: {ts} &nbsp;|&nbsp; Status: <font color='{status_color}'><b>{st}</b></font>"
        story.append(Paragraph(meta_line, styles['Normal']))
        story.append(Spacer(1, 3))
        story.append(Preformatted(cd, code_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    
    filename = f"GITAMW_Lab_Report_{roll_num if roll_num != 'N/A' else 'Session'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
