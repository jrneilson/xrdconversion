#!/bin/bash

# Build script for macOS application
echo "Building XRD Format Converter for macOS..."

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install --upgrade pip

# Handle pathlib conflict in conda environments
echo "Checking for pathlib conflicts..."
pip uninstall pathlib -y 2>/dev/null || true

pip install pyinstaller
pip install py2app
pip install numpy matplotlib

# Try tkinterdnd2 for better drag-drop support (optional)
pip install tkinterdnd2 || echo "tkinterdnd2 installation failed (optional dependency)"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.app

# Build with PyInstaller (recommended)
echo "Building with PyInstaller..."
pyinstaller xrd_converter.spec

# Alternative: Build with py2app (uncomment if preferred)
# echo "Building with py2app..."
# python setup.py py2app

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Application created in: dist/"
    ls -la dist/
    
    # Create DMG (optional)
    echo "Creating DMG installer..."
    if command -v create-dmg &> /dev/null; then
        create-dmg \
            --volname "XRD Format Converter" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --app-drop-link 425 120 \
            "XRD_Format_Converter_macOS.dmg" \
            "dist/"
    else
        echo "create-dmg not found. Install with: brew install create-dmg"
        echo "Creating simple DMG..."
        hdiutil create -volname "XRD Format Converter" -srcfolder dist/ -ov -format UDZO XRD_Format_Converter_macOS.dmg
    fi
else
    echo "Build failed!"
    exit 1
fi

echo "macOS build complete!"