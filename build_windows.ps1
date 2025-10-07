# PowerShell build script for Windows executable (no admin required)
# Alternative to build_windows.bat

Write-Host "Building XRD Format Converter for Windows..." -ForegroundColor Green
Write-Host "Note: No administrator privileges required" -ForegroundColor Yellow

# Function to check Python version
function Test-PythonVersion {
    param($pythonCmd)
    try {
        $version = & $pythonCmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -eq 3 -and $minor -ge 8) {
                return $true
            }
        }
    } catch {
        return $false
    }
    return $false
}

# Find suitable Python installation
$pythonCmd = $null
$pythonCandidates = @("python3", "python", "py -3.11", "py -3.10", "py -3.9", "py -3.8", "py -3")

Write-Host "Searching for suitable Python installation..." -ForegroundColor Yellow

foreach ($candidate in $pythonCandidates) {
    Write-Host "Trying: $candidate" -ForegroundColor Gray
    if (Test-PythonVersion $candidate) {
        $pythonCmd = $candidate
        $version = & $candidate --version 2>&1
        Write-Host "✓ Found suitable Python: $version" -ForegroundColor Green
        Write-Host "Using command: $pythonCmd" -ForegroundColor Green
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "✗ Error: No suitable Python installation found" -ForegroundColor Red
    Write-Host "Requirements: Python 3.8 or higher" -ForegroundColor Yellow
    Write-Host "Please install Python 3.8+ from python.org and add it to PATH" -ForegroundColor Yellow
    
    # Show what Python versions are available
    Write-Host "`nPython installations found:" -ForegroundColor Yellow
    try { $ver = python --version 2>&1; Write-Host "  python: $ver" } catch { Write-Host "  python: Not found" }
    try { $ver = python3 --version 2>&1; Write-Host "  python3: $ver" } catch { Write-Host "  python3: Not found" }
    try { $ver = py --version 2>&1; Write-Host "  py: $ver" } catch { Write-Host "  py launcher: Not found" }
    
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonCmd.Split(' ') -m venv venv
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