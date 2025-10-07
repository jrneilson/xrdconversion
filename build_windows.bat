@echo off
REM Build script for Windows executable (no admin required)

echo Building XRD Format Converter for Windows...
echo Note: No administrator privileges required

REM Function to check Python version
call :check_python_version

REM Check if a suitable Python is available
if "%PYTHON_CMD%"=="" (
    echo Error: No suitable Python installation found
    echo Please install Python 3.8+ from python.org and add it to PATH
    echo Current Python found: 
    python --version 2>nul || echo   None found
    pause
    exit /b 1
)

echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
goto :main

:check_python_version
REM Try different Python commands to find a suitable version
set PYTHON_CMD=

REM Try python3 first (preferred)
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do (
        set VERSION=%%i
        call :check_version_number
        if not errorlevel 1 (
            set PYTHON_CMD=python3
            goto :eof
        )
    )
)

REM Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        set VERSION=%%i
        call :check_version_number
        if not errorlevel 1 (
            set PYTHON_CMD=python
            goto :eof
        )
    )
)

REM Try py launcher with specific versions
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.11
    goto :eof
)

py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.10
    goto :eof
)

py -3.9 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.9
    goto :eof
)

py -3.8 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.8
    goto :eof
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :eof
)

goto :eof

:check_version_number
REM Check if version is 3.8 or higher
for /f "tokens=1,2 delims=." %%a in ("%VERSION%") do (
    if %%a geq 3 (
        if %%b geq 8 (
            exit /b 0
        )
    )
)
exit /b 1

:main

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
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