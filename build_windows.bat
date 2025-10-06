@echo off
REM Build script for Windows executable (no admin required)

echo Building XRD Format Converter for Windows...
echo Note: No administrator privileges required

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from python.org and add it to PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required packages (virtual environment doesn't need --user)
echo Installing dependencies in virtual environment...
python -m pip install --upgrade pip

REM Handle pathlib conflict in conda environments
echo Checking for pathlib conflicts...
pip uninstall pathlib -y >nul 2>&1

REM Install packages in virtual environment (no admin needed)
echo Installing PyInstaller and dependencies...
pip install pyinstaller
pip install numpy matplotlib

REM Try tkinterdnd2 for better drag-drop support (optional)
echo Installing optional drag-drop support...
pip install tkinterdnd2
if %errorlevel% neq 0 (
    echo Note: tkinterdnd2 installation failed (optional dependency)
    echo Drag-and-drop will fall back to file selection dialog
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.exe" del *.exe

REM Build with PyInstaller
echo Building with PyInstaller...
pyinstaller xrd_converter.spec

if %errorlevel% equ 0 (
    echo Build successful!
    echo Executable created in: dist\
    dir dist\
    
    REM Create installer with NSIS (if available)
    echo Checking for NSIS installer...
    where makensis >nul 2>&1
    if %errorlevel% equ 0 (
        echo Creating Windows installer...
        REM Note: You would need to create an NSIS script here
        echo NSIS found but installer script not implemented
        echo You can create an NSIS script to package the executable
    ) else (
        echo NSIS not found. Install NSIS to create Windows installer
        echo Executable is available in dist\ folder
    )
) else (
    echo Build failed!
    pause
    exit /b 1
)

echo Windows build complete!
pause