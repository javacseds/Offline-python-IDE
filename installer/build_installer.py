"""
GITAMW Python Smart IDE - One-Click Build Script
=================================================
Gouthami Institute of Technology and Management for Women (Autonomous)
Department of Computer Science & Engineering

Steps performed:
  1. Generate icon assets (icon.ico, wizard banners)
  2. Run PyInstaller to bundle the app
  3. Remind user to run Inno Setup for the final installer .exe

Usage:
    python installer/build_installer.py
"""

import os
import sys
import shutil
import subprocess

# ─── Resolve paths ────────────────────────────────────────────────────────
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR      = os.path.dirname(INSTALLER_DIR)
ASSETS_DIR    = os.path.join(INSTALLER_DIR, "assets")
DIST_DIR      = os.path.join(INSTALLER_DIR, "dist")
BUILD_DIR     = os.path.join(INSTALLER_DIR, "build")
SPEC_FILE     = os.path.join(INSTALLER_DIR, "gitamw_ide.spec")
ISS_FILE      = os.path.join(INSTALLER_DIR, "gitamw_ide_setup.iss")


def banner(msg):
    print("\n" + "=" * 65)
    print(f"  {msg}")
    print("=" * 65)


# ─── Step 1: Generate icon assets ─────────────────────────────────────────
def generate_assets():
    banner("STEP 1 — Generating icon & banner assets")
    os.makedirs(ASSETS_DIR, exist_ok=True)

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  [WARN] Pillow not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, ImageDraw, ImageFont

    # ── App icon (256×256) ──────────────────────────────────────────────
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = []
    for sz in ico_sizes:
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Dark blue circle background
        draw.ellipse([1, 1, sz - 2, sz - 2], fill="#1e3a8a")
        # "Py" text (scaled)
        font_size = max(8, sz // 3)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        text = "Py"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((sz - tw) // 2, (sz - th) // 2), text, fill="#f97316", font=font)
        frames.append(img)

    icon_path = os.path.join(ASSETS_DIR, "icon.ico")
    frames[0].save(
        icon_path,
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=frames[1:],
    )
    print(f"  [OK] Icon saved: {icon_path}")

    # ── Wizard banner (494×314 BMP) ─────────────────────────────────────
    banner_img = Image.new("RGB", (494, 314), "#1e3a8a")
    draw = ImageDraw.Draw(banner_img)
    # Gradient bands
    for y in range(314):
        r = int(30  + (y / 314) * 20)
        g = int(58  + (y / 314) * 20)
        b = int(138 + (y / 314) * 30)
        draw.line([(0, y), (494, y)], fill=(r, g, b))
    # College name text
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 20)
        sub_font   = ImageFont.truetype("arial.ttf",   13)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font   = title_font

    draw.text((30, 30),  "GITAMW Python Smart IDE",                     fill="white",   font=title_font)
    draw.text((30, 60),  "Gouthami Institute of Technology",             fill="#93c5fd", font=sub_font)
    draw.text((30, 78),  "and Management for Women (Autonomous)",        fill="#93c5fd", font=sub_font)
    draw.text((30, 96),  "Dept. of Computer Science & Engineering",      fill="#fbbf24", font=sub_font)
    draw.text((30, 130), "Offline Python IDE — No Internet Required",    fill="#86efac", font=sub_font)

    banner_path = os.path.join(ASSETS_DIR, "wizard_banner.bmp")
    banner_img.save(banner_path, format="BMP")
    print(f"  [OK] Wizard banner saved: {banner_path}")

    # ── Wizard small icon (55×55 BMP) ────────────────────────────────────
    small_img = Image.new("RGB", (55, 55), "#1e3a8a")
    draw2 = ImageDraw.Draw(small_img)
    draw2.ellipse([2, 2, 53, 53], fill="#1e3a8a", outline="#f97316", width=2)
    small_path = os.path.join(ASSETS_DIR, "wizard_icon.bmp")
    small_img.save(small_path, format="BMP")
    print(f"  [OK] Wizard icon saved: {small_path}")


# ─── Step 2: Run PyInstaller ───────────────────────────────────────────────
def build_exe():
    banner("STEP 2 — Running PyInstaller (this may take 2-5 minutes)")

    # Clean previous build
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
        print("  [DEL] Removed old dist/ folder")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
        print("  [DEL] Removed old build/ folder")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        SPEC_FILE,
    ]

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=INSTALLER_DIR)

    if result.returncode != 0:
        print("\n  [ERR] PyInstaller build FAILED!")
        print("     Check the output above for errors.")
        sys.exit(1)

    exe_path = os.path.join(DIST_DIR, "GITAMW_Smart_IDE.exe")  # onefile mode: directly in dist/
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n  [OK] Build SUCCESS!")
        print(f"  EXE Location: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"\n  --> Copy GITAMW_Smart_IDE.exe to any computer and double-click to run!")
    else:
        print(f"     [WARN] EXE not found at: {exe_path}")


# --- Step 3: Instructions for Inno Setup ----------------------------------
def print_inno_instructions():
    banner("STEP 3 - Build Installer with Inno Setup")
    print("""
  To create the final Setup_GITAMW_Python_IDE.exe installer:

  Option A - Inno Setup GUI (Recommended):
  -----------------------------------------
  1. Download Inno Setup (free):
     https://jrsoftware.org/isdl.php

  2. Install and open Inno Setup Compiler.

  3. Open the script file:
     installer\\gitamw_ide_setup.iss

  4. Click:  Build -> Compile  (or press F9)

  5. Find your installer at:
     installer\\setup_output\\Setup_GITAMW_Python_IDE_v1.0.0.exe

  Option B - Command Line (if Inno Setup is already installed):
  --------------------------------------------------------------
     "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" installer\\gitamw_ide_setup.iss

  -----------------------------------------------------------------
  The installer will provide:
    [OK] Windows Installer (.exe)
    [OK] Desktop Shortcut
    [OK] Start Menu Shortcut
    [OK] Automatic Browser Launch on first run
    [OK] Full Uninstaller (Add/Remove Programs)
    [OK] No command prompt / console window
  -----------------------------------------------------------------
""")



# ─── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  GITAMW Python Smart IDE — Installer Build Tool")
    print("  Gouthami Institute of Technology (Autonomous)")
    print("  Dept. of CSE")
    print("=" * 65)

    generate_assets()
    build_exe()
    print_inno_instructions()
