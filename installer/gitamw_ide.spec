# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# GITAMW Python Smart IDE - PyInstaller Spec File
# Gouthami Institute of Technology and Management for Women (Autonomous)
# Department of Computer Science & Engineering
# =============================================================================

import os
import sys

block_cipher = None

# Resolve project root (one level up from installer/)
SPEC_DIR  = os.path.abspath(SPECPATH)           # d:\offline_python_interface\installer
ROOT_DIR  = os.path.dirname(SPEC_DIR)           # d:\offline_python_interface

a = Analysis(
    [os.path.join(SPEC_DIR, 'app_launcher.py')],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=[
        # Bundle the entire app package
        (os.path.join(ROOT_DIR, 'app'),              'app'),
        # Bundle Jinja2 templates
        (os.path.join(ROOT_DIR, 'app', 'templates'), 'app/templates'),
        # Bundle static files (CSS, JS)
        (os.path.join(ROOT_DIR, 'app', 'static'),    'app/static'),
        # Bundle pre-loaded sample programs
        (os.path.join(ROOT_DIR, 'sample_programs'),  'sample_programs'),
        # Bundle data directory (settings, students, history)
        (os.path.join(ROOT_DIR, 'data'),             'data'),
    ],
    hiddenimports=[
        # FastAPI & Starlette
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
        'uvicorn.lifespan',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.logging',
        # AnyIO / async
        'anyio',
        'anyio._backends._asyncio',
        # Jinja2 templating
        'jinja2',
        'jinja2.ext',
        # Python-multipart
        'multipart',
        # Pydantic
        'pydantic',
        'pydantic.v1',
        # App modules
        'app',
        'app.main',
        'app.execution_engine',
        'app.file_manager',
        'app.storage_manager',
        'app.package_manager',
        'app.smart_error_explainer',
        # ReportLab PDF
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.platypus',
        # Standard libs
        'email.mime.multipart',
        'email.mime.text',
        'multiprocessing',
        'ctypes',
        'ctypes.wintypes',
        'ctypes.windll',
        # Tray icon (graceful if absent)
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',   # only needed at runtime by user code - not the IDE itself
        'numpy',
        'pandas',
        'test',
        'unittest',
        'distutils',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GITAMW_Smart_IDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # ← NO console window (silent background process)
    windowed=True,          # ← Windowed application (no cmd prompt)
    icon=os.path.join(SPEC_DIR, 'assets', 'icon.ico'),
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GITAMW_Smart_IDE',
)
