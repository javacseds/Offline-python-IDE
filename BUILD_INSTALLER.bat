@echo off
:: =============================================================================
:: GITAMW Python Smart IDE - One-Click Build Launcher
:: Double-click this file to build the Windows installer
:: =============================================================================

title GITAMW IDE Installer Builder

echo.
echo  ====================================================================
echo   GITAMW Python Smart IDE - Installer Builder
echo   Gouthami Institute of Technology and Management for Women
echo   Department of Computer Science and Engineering
echo  ====================================================================
echo.

:: Change to the project root directory
cd /d "%~dp0.."

:: Run the build script
python installer\build_installer.py

echo.
echo  ====================================================================
echo   Build process complete. Press any key to close.
echo  ====================================================================
pause
