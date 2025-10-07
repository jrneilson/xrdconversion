# XRD Format Converter - Build Instructions

This document provides instructions for building the XRD Format Converter application for macOS and Windows.

## Prerequisites

### For macOS:
- macOS 10.12 or later
- Python 3.8 or later
- Xcode Command Line Tools (`xcode-select --install`)
- Homebrew (optional, for DMG creation)

### For Windows:
- Windows 10 or later
- Python 3.8 or later
- Visual C++ Build Tools (usually included with Python)

## Building the Application

### macOS Application Bundle

1. **Clone or download the project:**
   ```bash
   cd /path/to/xrdFormatConverter
   ```

2. **Run the build script:**
   ```bash
   ./build_mac.sh
   ```

3. **The script will:**
   - Create a virtual environment
   - Install dependencies (PyInstaller, py2app, numpy, matplotlib)
   - Build the application using PyInstaller
   - Create a DMG installer (if create-dmg is available)

4. **Output:**
   - Application: `dist/XRD Format Converter.app`
   - DMG installer: `XRD_Format_Converter_macOS.dmg`

### Windows Executable

**Option A: Using Command Prompt (Batch Script)**

1. **Open Command Prompt (no admin privileges required)**

2. **Navigate to the project directory:**
   ```cmd
   cd C:\path\to\xrdFormatConverter
   ```

3. **Run the build script:**
   ```cmd
   build_windows.bat
   ```

**Option B: Using PowerShell (Recommended)**

1. **Open PowerShell (no admin privileges required)**

2. **Navigate to the project directory:**
   ```powershell
   cd C:\path\to\xrdFormatConverter
   ```

3. **Set execution policy (if needed):**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Run the build script:**
   ```powershell
   .\build_windows.ps1
   ```

4. **The script will:**
   - Create a virtual environment
   - Install dependencies (PyInstaller, numpy, matplotlib)
   - Build the executable using PyInstaller

5. **Output:**
   - Executable: `dist\XRD_Format_Converter.exe`

## Manual Build Process

If the automated scripts don't work, you can build manually:

### Manual macOS Build

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pyinstaller numpy matplotlib tkinterdnd2

# Build application
pyinstaller xrd_converter.spec

# Or alternative method with py2app
pip install py2app
python setup.py py2app
```

### Manual Windows Build

```cmd
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install pyinstaller numpy matplotlib tkinterdnd2

# Build executable
pyinstaller xrd_converter.spec
```

## Troubleshooting

### Common Issues

1. **Missing tkinter:**
   - On some Linux distributions: `sudo apt-get install python3-tk`
   - On macOS with Homebrew Python: `brew install python-tk`

2. **PyInstaller pathlib conflict (conda environments):**
   ```bash
   conda remove pathlib
   # or use a fresh virtual environment:
   python3 -m venv clean_venv
   source clean_venv/bin/activate
   ```

3. **PyInstaller import errors:**
   - Add missing modules to `hiddenimports` in `xrd_converter.spec`
   - Try building with `--onefile` flag

4. **matplotlib backend issues:**
   - Set backend explicitly: `import matplotlib; matplotlib.use('TkAgg')`

5. **Drag-and-drop not working:**
   - Install tkinterdnd2: `pip install tkinterdnd2`
   - Fallback to file selection dialog if drag-drop fails

### Build Errors

1. **"Permission denied" on macOS:**
   ```bash
   chmod +x build_mac.sh
   ```

2. **Python 2.7 found instead of Python 3:**
   - Problem: System has old Python 2.7 as default `python` command
   - Solution: Install Python 3.8+ from python.org or use Python launcher:
     ```cmd
     py -3 --version  # Check if Python 3 is available
     ```
   - The build scripts now automatically detect suitable Python versions

3. **Python not found on Windows:**
   - Install Python from python.org
   - Add Python to PATH during installation
   - No administrator privileges required

4. **Missing Visual C++ tools on Windows:**
   - Install Microsoft C++ Build Tools
   - Or install Visual Studio Community
   - These are usually included with modern Python installations

5. **Permission issues on Windows:**
   - The build script uses virtual environments (no admin needed)
   - If you get permission errors, ensure your user has write access to the project folder
   - Avoid running as administrator unless absolutely necessary

6. **"No module named venv" error:**
   - This indicates Python 2.7 is being used
   - Install Python 3.8+ or use the Python launcher: `py -3`
   - The updated build scripts handle this automatically

## Distribution

### macOS Distribution
- The `.app` bundle can be distributed directly
- The DMG file provides a more professional installer experience
- For App Store distribution, you'll need Apple Developer Program membership

### Windows Distribution
- The `.exe` file is standalone and can be distributed directly
- Consider creating an NSIS installer for professional distribution
- For Microsoft Store distribution, additional packaging is required

## File Associations (Optional)

### macOS
The app bundle includes file associations for .brml and .raw files. Users can:
- Right-click files → "Open with" → XRD Format Converter
- Set as default application in Finder

### Windows
To associate file types:
1. Right-click a .brml or .raw file
2. Choose "Open with" → "Choose another app"
3. Select the XRD Format Converter executable
4. Check "Always use this app"

## Performance Notes

- First launch may be slower due to Python runtime initialization
- Conversion speed depends on file size and system performance
- GUI remains responsive during conversion thanks to threading

## Security Notes

- The application doesn't require special permissions
- No network access required
- All file processing is done locally
- Metadata extraction is read-only