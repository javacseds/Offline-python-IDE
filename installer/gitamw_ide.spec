# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# GITAMW Python Smart IDE - PyInstaller Spec (ONEFILE mode)
# Produces: GITAMW_Smart_IDE.exe  (single self-contained executable)
# Gouthami Institute of Technology and Management for Women (Autonomous)
# Department of Computer Science & Engineering
# =============================================================================

import os

block_cipher = None

SPEC_DIR = os.path.abspath(SPECPATH)        # ...\installer\
ROOT_DIR = os.path.dirname(SPEC_DIR)        # ...\offline_python_interface\

a = Analysis(
    [os.path.join(SPEC_DIR, 'app_launcher.py')],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=[
        # App package (Python modules)
        (os.path.join(ROOT_DIR, 'app'),             'app'),
        # Jinja2 HTML templates
        (os.path.join(ROOT_DIR, 'app', 'templates'),'app/templates'),
        # Static files (CSS, JS)
        (os.path.join(ROOT_DIR, 'app', 'static'),   'app/static'),
        # Pre-loaded lab sample programs
        (os.path.join(ROOT_DIR, 'sample_programs'), 'sample_programs'),
    ],
    hiddenimports=[
        # FastAPI / Starlette
        'fastapi',
        'starlette',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.templating',
        'starlette.staticfiles',
        'starlette.responses',
        # Uvicorn
        'uvicorn',
        'uvicorn.main',
        'uvicorn.config',
        'uvicorn.server',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.logging',
        # Async
        'anyio',
        'anyio._backends._asyncio',
        # Jinja2
        'jinja2',
        'jinja2.ext',
        # Pydantic
        'pydantic',
        # ReportLab PDF
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.platypus',
        # App modules
        'app',
        'app.main',
        'app.execution_engine',
        'app.file_manager',
        'app.storage_manager',
        'app.package_manager',
        'app.smart_error_explainer',
        # PIL (for tray icon)
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        # System
        'multiprocessing',
        'ctypes',
        'email.mime.multipart',
        'email.mime.text',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── ONEFILE EXE: bundle everything into a single .exe ──────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,         # include all binaries directly in the exe
    a.zipfiles,
    a.datas,            # include all data files directly in the exe
    [],
    name='GITAMW_Smart_IDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # NO console window
    windowed=True,      # windowed application
    icon=os.path.join(SPEC_DIR, 'assets', 'icon.ico'),
    version_file=None,
)
# NOTE: No COLLECT block = ONEFILE mode
