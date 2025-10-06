# PowerShell build script for Windows executable (no admin required)
# Alternative to build_windows.bat

Write-Host "Building XRD Format Converter for Windows..." -ForegroundColor Green
Write-Host "Note: No administrator privileges required" -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from python.org and add it to PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install required packages
Write-Host "Installing dependencies in virtual environment..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Handle pathlib conflict in conda environments
Write-Host "Checking for pathlib conflicts..." -ForegroundColor Yellow
try {
    pip uninstall pathlib -y 2>$null
} catch {
    # Ignore errors if pathlib isn't installed
}

# Install packages in virtual environment (no admin needed)
Write-Host "Installing PyInstaller and dependencies..." -ForegroundColor Yellow
pip install pyinstaller
pip install numpy matplotlib

# Try tkinterdnd2 for better drag-drop support (optional)
Write-Host "Installing optional drag-drop support..." -ForegroundColor Yellow
try {
    pip install tkinterdnd2
    Write-Host "tkinterdnd2 installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Note: tkinterdnd2 installation failed (optional dependency)" -ForegroundColor Yellow
    Write-Host "Drag-and-drop will fall back to file selection dialog" -ForegroundColor Yellow
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Get-ChildItem -Filter "*.exe" | Remove-Item -Force

# Build with PyInstaller
Write-Host "Building with PyInstaller..." -ForegroundColor Yellow
pyinstaller xrd_converter.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable created in: dist\" -ForegroundColor Green
    Get-ChildItem "dist\"
    
    # Check for NSIS installer
    Write-Host "Checking for NSIS installer..." -ForegroundColor Yellow
    try {
        Get-Command makensis -ErrorAction Stop
        Write-Host "NSIS found but installer script not implemented" -ForegroundColor Yellow
        Write-Host "You can create an NSIS script to package the executable" -ForegroundColor Yellow
    } catch {
        Write-Host "NSIS not found. Install NSIS to create Windows installer" -ForegroundColor Yellow
        Write-Host "Executable is available in dist\ folder" -ForegroundColor Green
    }
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Windows build complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"