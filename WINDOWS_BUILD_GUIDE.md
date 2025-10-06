# Quick Windows Build Guide

## No Administrator Rights Required! 🎉

This guide shows you how to build the XRD Format Converter on Windows **without** needing administrator privileges.

## Prerequisites

1. **Python 3.8+** - Download from [python.org](https://python.org)
   - ✅ Check "Add Python to PATH" during installation
   - ❌ No admin rights needed for user installation

2. **Project Files** - Download or clone this repository

## Quick Build (Choose One Method)

### Method 1: PowerShell (Recommended)
```powershell
# Navigate to the project folder
cd C:\path\to\xrdFormatConverter

# Allow script execution (one-time setup)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the build script
.\build_windows.ps1
```

### Method 2: Command Prompt
```cmd
# Navigate to the project folder
cd C:\path\to\xrdFormatConverter

# Run the build script
build_windows.bat
```

## What the Scripts Do

1. **Create Virtual Environment** - Isolated Python environment (no admin needed)
2. **Install Dependencies** - PyInstaller, NumPy, Matplotlib, etc.
3. **Build Executable** - Creates standalone .exe file
4. **Package Application** - Ready-to-distribute executable

## Output

After successful build:
- **Executable**: `dist\XRD_Format_Converter.exe`
- **Size**: ~50-100 MB (includes all dependencies)
- **Portable**: Can be copied to other Windows computers

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure "Add to PATH" was checked during installation
- Restart Command Prompt/PowerShell

### "Execution policy" error (PowerShell only)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Permission denied" errors
- Don't run as administrator
- Make sure you have write access to the project folder
- Try building in a folder under your user directory (e.g., `C:\Users\YourName\`)

### Virtual environment issues
```cmd
# Clean up and start over
rmdir /s venv
# Then run the build script again
```

## Distribution

The built executable:
- ✅ **Standalone** - No Python installation required on target computers
- ✅ **No Admin Required** - Regular users can run it
- ✅ **Portable** - Copy the .exe file anywhere
- ✅ **Windows 10/11** - Compatible with modern Windows versions

## File Associations (Optional)

To make .brml and .raw files open with your converter:
1. Right-click a .brml or .raw file
2. Choose "Open with" → "Choose another app"
3. Browse to your built .exe file
4. Check "Always use this app"

## Performance Notes

- **First Launch**: May take 5-10 seconds (Python runtime startup)
- **File Conversion**: Fast (depends on file size)
- **Memory Usage**: ~50-100 MB (normal for bundled Python apps)

## Security

- **No Network Access**: All processing done locally
- **No Admin Rights**: Runs with user privileges only
- **Open Source**: All code is visible and auditable
- **Safe**: No system modifications required