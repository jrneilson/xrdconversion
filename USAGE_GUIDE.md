# XRD Format Converter - Usage Guide

## Overview

The XRD Format Converter is a cross-platform application that converts BRML and RAW X-ray diffraction files to the standard XYE format (three-column: two-theta, intensity, error).

## Features

- **Drag-and-Drop Interface**: Simply drag BRML or RAW files onto the application
- **File Selection Dialog**: Use the "Select Files" button to browse for files
- **Batch Processing**: Convert multiple files at once
- **Progress Tracking**: Real-time progress bar and status updates
- **Metadata Extraction**: Automatically extracts and saves metadata to .metadata files
- **Cross-Platform**: Works on macOS, Windows, and Linux

## Getting Started

### Option 1: Using Pre-built Applications

#### macOS
1. Download `XRD_Format_Converter_macOS.dmg`
2. Double-click to mount the disk image
3. Drag "XRD Format Converter" to your Applications folder
4. Launch from Applications or Launchpad

#### Windows
1. Download `XRD_Format_Converter.exe`
2. Double-click to run (no installation required)
3. Windows may show a security warning for unsigned applications

### Option 2: Running from Source

```bash
# Clone or download the project
cd xrdFormatConverter

# Install dependencies
pip install numpy matplotlib tkinterdnd2

# Run the GUI application
python xrd_converter_gui.py

# Or run the command-line version
python xrd_converter.py input_file.brml
```

## Using the Application

### 1. Starting the Application
- **macOS**: Double-click the app in Applications folder
- **Windows**: Double-click the .exe file
- **Source**: Run `python xrd_converter_gui.py`

### 2. Adding Files to Convert

#### Method A: Drag and Drop
1. Open the XRD Format Converter application
2. Drag .brml or .raw files from Finder/Explorer
3. Drop them onto the blue drop zone in the application
4. Files will appear in the "Selected Files" list

#### Method B: File Selection Dialog  
1. Click the "Select Files" button
2. Browse to your XRD data files
3. Select one or more .brml or .raw files
4. Click "Open"

### 3. Converting Files
1. After adding files, click "Convert Files"
2. Watch the progress bar and status updates
3. Check the conversion log for detailed results
4. Converted files will be saved in the same directory as the source files

### 4. Output Files
For each input file, two output files are created:

- **XYE File**: `filename.xye` - Three-column data (2θ, intensity, error)
- **Metadata File**: `filename.metadata` - Extracted metadata and statistics

Example:
```
Input:  GTT-01-02_Mn2ZnN2.brml
Output: GTT-01-02_Mn2ZnN2.xye
        GTT-01-02_Mn2ZnN2.metadata
```

## XYE File Format

The XYE format is a standard three-column ASCII format:
```
# XRD data converted from: GTT-01-02_Mn2ZnN2.brml
# Two-Theta  Intensity  Error
5.0000      1234.56    35.13
5.0180      1245.78    35.29
5.0360      1189.45    34.49
...
```

Where:
- **Column 1**: Two-theta angles (degrees)
- **Column 2**: Intensity values (counts)  
- **Column 3**: Error values (√intensity, Poisson statistics)

## Metadata File Contents

The .metadata file contains:
- Original file information
- Measurement parameters (when available)
- Data range and statistics
- Processing timestamps

Example:
```
# XRD File Metadata
# Extracted from source file

SOURCE_FILE: GTT-01-02_Mn2ZnN2.brml
CONVERSION_DATE: 2024-01-15 14:30:25

# Data Summary
DATA_POINTS: 1399
TWO_THETA_RANGE: 5.000 - 30.000
INTENSITY_RANGE: 45.000 - 8096.000
```

## Supported File Types

### BRML Files (.brml)
- XML-based format from Bruker diffractometers
- Contains measurement data and metadata
- Compressed archive format

### RAW Files (.raw)  
- Binary format from various XRD instruments
- Contains binary data with text headers
- Legacy format support

## Troubleshooting

### Common Issues

1. **File not recognized**
   - Check file extension (.brml or .raw)
   - Ensure file is not corrupted
   - Try the command-line version for detailed error messages

2. **Conversion fails**
   - Check the conversion log for specific error messages
   - Verify input file integrity
   - Some proprietary formats may not be supported

3. **Drag-and-drop not working**
   - Use the "Select Files" button as alternative
   - On some systems, tkinterdnd2 may not be available
   - Restart the application if drag-drop stops working

4. **Application won't start**
   - **macOS**: Right-click → "Open" to bypass security warnings
   - **Windows**: Run as administrator if needed
   - Check that all dependencies are installed for source version

### Getting Help

1. Check the conversion log for detailed error messages
2. Try the command-line version: `python xrd_converter.py yourfile.brml`
3. Verify file format with a text editor or hex viewer
4. Report issues with sample files for debugging

## Tips for Best Results

1. **File Organization**: Keep source files organized in folders
2. **Batch Processing**: Process multiple files at once for efficiency  
3. **Backup Originals**: Keep original files as backups
4. **Check Outputs**: Verify converted data looks reasonable
5. **Metadata Review**: Check .metadata files for processing details

## Performance Notes

- **Large Files**: Processing time scales with file size
- **Multiple Files**: Files are processed sequentially
- **Memory Usage**: Large datasets may require sufficient RAM
- **First Launch**: Initial startup may be slower (especially Windows .exe)

## Command Line Usage

For advanced users, the converter can be used from command line:

```bash
# Convert single file
python xrd_converter.py input.brml

# Convert multiple files
python xrd_converter.py file1.brml file2.raw file3.brml

# Show help
python xrd_converter.py --help
```

## Integration with Analysis Software

The XYE format is compatible with:
- **MATCH!** - Phase identification software
- **TOPAS** - Rietveld refinement
- **JANA** - Structure refinement
- **FullProf** - Powder diffraction analysis
- **GSAS-II** - General structure analysis
- **Origin/Excel** - Data plotting and analysis