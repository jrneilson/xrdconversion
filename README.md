# XRD Format Converter

A Python utility to convert X-ray diffraction (XRD) data files from BRML or RAW formats to XYE format with metadata extraction.

## Features

- Converts BRML (XML-based zip format) and RAW (binary format) files to XYE format
- Extracts XRD measurement data (2theta, intensity)
- Calculates statistical errors using Poisson statistics
- Saves metadata to separate files
- Generates 3-column XYE files (two-theta, intensity, error)

## Usage

### Command Line

```bash
python3 xrd_converter.py file1.brml file2.raw [--verbose]
```

Or make it executable and run directly:

```bash
chmod +x xrd_converter.py
./xrd_converter.py file1.brml file2.raw [--verbose]
```

### Arguments

- `files`: One or more BRML or RAW files to convert
- `--verbose` or `-v`: Enable verbose output

## Output Files

For each input file `sample.raw` or `sample.brml`, the converter creates:

1. **`sample.xye`** - XYE format file with three columns:
   - Column 1: Two-theta angle (degrees)
   - Column 2: Intensity (counts)
   - Column 3: Statistical error (sqrt of intensity, minimum 1.0)

2. **`sample.metadata`** - Metadata file containing:
   - Extracted metadata from the source file
   - Data summary (number of points, ranges)
   - Measurement parameters

## XYE Format

The XYE format is a simple 3-column ASCII format commonly used in XRD analysis:

```
# Two-Theta Intensity Error
10.000000 1250.000000 35.355339
10.020000 1248.000000 35.328135
10.040000 1251.000000 35.369774
...
```

## Supported File Types

### BRML Files
- XML-based zip archives containing XRD measurement data
- Extracts data from embedded XML files
- Supports metadata extraction from XML structure

### RAW Files
- Binary format files from XRD instruments
- Extracts intensity data from binary sections
- Parses text headers for metadata
- Generates 2theta arrays based on typical XRD ranges

## Examples

Convert a single file:
```bash
python3 xrd_converter.py GTT-01-02_Mn2ZnN2.raw
```

Convert multiple files with verbose output:
```bash
python3 xrd_converter.py *.brml *.raw --verbose
```

## Output Example

After conversion, you'll see files like:
- `GTT-01-02_Mn2ZnN2.xye` - Main XRD data in XYE format
- `GTT-01-02_Mn2ZnN2.metadata` - Extracted metadata and parameters

## Dependencies

- Python 3.6+
- numpy
- xml.etree.ElementTree (built-in)
- zipfile (built-in)
- struct (built-in)
- argparse (built-in)

## Installation

No installation required. Just download `xrd_converter.py` and run it with Python 3.

## Notes

- The converter uses Poisson statistics for error calculation: error = sqrt(intensity)
- Minimum error value is set to 1.0 to avoid zero errors
- For RAW files without explicit angle ranges, typical XRD ranges (10-80°) are assumed
- Binary data extraction handles different endianness and data layouts
- BRML files are processed as zip archives containing XML measurement data

## Troubleshooting

If conversion fails:
1. Check that the input file exists and is readable
2. Verify the file extension matches the format (.brml or .raw)
3. Use `--verbose` flag to see detailed conversion information
4. Check that the file is not corrupted

For questions or issues, refer to the source code comments for implementation details.