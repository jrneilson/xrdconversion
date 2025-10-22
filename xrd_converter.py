#!/usr/bin/env python3
"""
XRD Format Converter
Converts BRML or RAW XRD files to XYE format (two theta, intensity, error).
Extracts metadata to separate files.
"""

import struct
import xml.etree.ElementTree as ET
import zipfile
import re
import argparse
from pathlib import Path
import numpy as np


class XRDConverter:
    """Converter for XRD data files from BRML/RAW to XYE format."""
    
    def __init__(self):
        self.two_theta = []
        self.intensity = []
        self.error = []
        self.metadata = {}
    
    def read_brml_file(self, filepath):
        """Read and parse BRML file (XML-based zip format)."""
        try:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                # Look for measurement container XML
                xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                
                for xml_file in xml_files:
                    with zip_ref.open(xml_file) as xml_data:
                        tree = ET.parse(xml_data)
                        root = tree.getroot()
                        
                        # Extract metadata
                        self._extract_xml_metadata(root)
                        
                        # Extract measurement data
                        self._extract_xml_data(root)
                        
        except Exception as e:
            print(f"Error reading BRML file: {e}")
            return False
        
        return True
    
    def read_raw_file(self, filepath):
        """Read and parse RAW file (binary format)."""
        try:
            with open(filepath, 'rb') as f:
                # Read all data
                content = f.read()
                
                # Extract metadata from content
                self._extract_raw_metadata(content)
                
                # Parse RAW format - look for data patterns
                self._extract_raw_data(content)
                
        except Exception as e:
            print(f"Error reading RAW file: {e}")
            return False
        
        return True
    
    def _extract_xml_metadata(self, root):
        """Extract metadata from XML structure."""
        # Common metadata fields
        metadata_fields = [
            'SAMPLEID', 'USER', 'COMMENT', 'CREATOR', 'CREATOR_VERSION',
            'DATE', 'TIME', 'LAMBDA', 'ANODE', 'VOLTAGE', 'CURRENT'
        ]
        
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag in metadata_fields and elem.text:
                self.metadata[tag] = elem.text.strip()
            
            # Extract attributes as well
            for attr, value in elem.attrib.items():
                if attr in metadata_fields:
                    self.metadata[attr] = value
    
    def _extract_xml_data(self, root):
        """Extract measurement data from XML."""
        # Look for Datum elements in BRML files (common structure)
        datum_elements = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'Datum' and elem.text:
                datum_elements.append(elem.text.strip())
        
        if datum_elements:
            # Parse datum elements - format is typically: time,unknown,angle1,angle2,intensity
            angles = []
            intensities = []
            
            for datum in datum_elements:
                parts = datum.split(',')
                if len(parts) >= 5:
                    try:
                        # Extract 2theta angle (3rd column, 0-indexed as 2)
                        # and intensity (5th column, 0-indexed as 4)
                        # Format: time,unknown,2theta,theta,intensity
                        angle = float(parts[2])  # 2theta column (correct for XRD)
                        intensity = float(parts[4])  # intensity column
                        angles.append(angle)
                        intensities.append(intensity)
                    except (ValueError, IndexError):
                        continue
            
            if angles and intensities:
                self.two_theta = angles
                self.intensity = intensities
                print(f"Extracted {len(self.intensity)} data points from Datum elements")
                return
        
        # Fallback: Look for other data arrays in XML
        for elem in root.iter():
            if 'data' in elem.tag.lower() or 'intensity' in elem.tag.lower():
                if elem.text:
                    try:
                        # Try to parse as space or comma separated values
                        values = re.split(r'[,\s]+', elem.text.strip())
                        test_values = [float(v) for v in values[:10] if v]  # Test first 10
                        if len(test_values) >= 10:  # Looks like real data
                            self.intensity = [float(v) for v in values if v]
                    except ValueError:
                        continue
            
            if 'angle' in elem.tag.lower() or 'theta' in elem.tag.lower():
                if elem.text:
                    try:
                        values = re.split(r'[,\s]+', elem.text.strip())
                        test_values = [float(v) for v in values[:10] if v]  # Test first 10
                        if len(test_values) >= 10:  # Looks like real data
                            self.two_theta = [float(v) for v in values if v]
                    except ValueError:
                        continue
    
    def _extract_raw_metadata(self, content):
        """Extract metadata from RAW file content."""
        # Parse header for common fields - look at first 1000 bytes as text
        header = content[:1000].decode('ascii', errors='ignore')
        lines = header.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for key-value patterns
            if 'SAMPLEID' in line:
                parts = line.split()
                if len(parts) > 1:
                    self.metadata['SAMPLEID'] = ' '.join(parts[1:])
            elif 'USER' in line:
                parts = line.split()
                if len(parts) > 1:
                    self.metadata['USER'] = ' '.join(parts[1:])
            elif 'COMMENT' in line:
                parts = line.split()
                if len(parts) > 1:
                    self.metadata['COMMENT'] = ' '.join(parts[1:])
            elif 'CREATOR' in line:
                parts = line.split()
                if len(parts) > 1:
                    self.metadata['CREATOR'] = ' '.join(parts[1:])
            elif line.startswith('RAW'):
                # Extract version and date info
                parts = line.split()
                if len(parts) >= 3:
                    self.metadata['FORMAT'] = parts[0]
                    self.metadata['VERSION'] = parts[1]
                    if len(parts) >= 5:
                        self.metadata['DATE'] = parts[2]
                        self.metadata['TIME'] = parts[3]
        
        # Look for angle range in binary data
        # Search for known measurement range patterns
        if b'2Theta' in content:
            # Find the position and try to extract range
            pos = content.find(b'2Theta')
            
            # Look for float values around the 2Theta section
            # RAW files often have measurement parameters as floats
            potential_angles = []
            
            # Search around the 2Theta position for float values
            for offset in range(-200, 300, 4):
                try:
                    test_pos = pos + offset
                    if 0 <= test_pos < len(content) - 4:
                        val = struct.unpack('<f', content[test_pos:test_pos+4])[0]
                        # Look for reasonable 2theta values
                        if 5 <= val <= 150:
                            potential_angles.append(val)
                except:
                    continue
            
            # If we found potential angle values, use them
            if len(potential_angles) >= 2:
                # Remove duplicates and sort
                angles = sorted(list(set(potential_angles)))
                if len(angles) >= 2:
                    self.metadata['START_ANGLE'] = str(angles[0])
                    self.metadata['END_ANGLE'] = str(angles[-1])
                    print(f"Found potential angle range: {angles[0]:.2f} - {angles[-1]:.2f}")
        
        # Also try to find step size or number of points
        # Look for reasonable step sizes (0.01 - 0.1 degrees)
        if b'STEP' in content or b'Step' in content:
            step_pos = content.find(b'STEP') if b'STEP' in content else content.find(b'Step')
            for offset in range(-50, 100, 4):
                try:
                    test_pos = step_pos + offset
                    if 0 <= test_pos < len(content) - 4:
                        val = struct.unpack('<f', content[test_pos:test_pos+4])[0]
                        if 0.005 <= val <= 0.2:  # Reasonable step size
                            self.metadata['STEP_SIZE'] = str(val)
                            break
                except:
                    continue
    
    def _extract_raw_data(self, content):
        """Extract measurement data from RAW file binary content."""
        # Look for measurement parameters first
        text_part = content[:1000].decode('ascii', errors='ignore')
        
        # Extract range parameters from metadata if available
        start_angle = 10.0  # Default
        end_angle = 80.0   # Default
        
        # Check if we found angle range in metadata
        if 'START_ANGLE' in self.metadata:
            try:
                start_angle = float(self.metadata['START_ANGLE'])
            except:
                pass
        if 'END_ANGLE' in self.metadata:
            try:
                end_angle = float(self.metadata['END_ANGLE'])
            except:
                pass
        
        # Look for angle parameters in text header
        if '2Theta' in text_part:
            # Try to extract from header
            import re
            angle_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', text_part)
            if angle_match:
                start_angle = float(angle_match.group(1))
                end_angle = float(angle_match.group(2))
        
        # For RAW files, intensity data is typically at the end of the file
        # The data appears to be 4-byte floats near the end
        file_size = len(content)
        
        # Try to extract from the last part of the file where real intensity data is
        # Based on the analysis, reasonable intensities are in the range 100-1000
        intensities = []
        
        # Work backwards from the end to find the data section
        for start_pos in range(file_size - 4000, max(0, file_size - 8000), -100):
            if start_pos < 0:
                start_pos = 0
            
            test_intensities = []
            try:
                for i in range(start_pos, file_size - 4, 4):
                    val = struct.unpack('<f', content[i:i+4])[0]
                    # Look for values in reasonable intensity range for XRD
                    if 50 <= val <= 10000:
                        test_intensities.append(val)
                    elif len(test_intensities) > 0:
                        # If we had good values but now don't, we might be done
                        break
                
                # If we found a good sequence of intensities, use it
                if len(test_intensities) > 100:
                    intensities = test_intensities
                    break
                    
            except:
                continue
        
        # If no good data found, try a simpler approach
        if not intensities:
            # Extract all floats from the second half of the file
            start_pos = file_size // 2
            for i in range(start_pos, file_size - 4, 4):
                try:
                    val = struct.unpack('<f', content[i:i+4])[0]
                    if 0 <= val <= 100000 and not (val < 1e-10 and val > 0):  # Skip very small values
                        intensities.append(val)
                except:
                    continue
        
        # If we found intensity data, generate corresponding 2theta values
        if intensities:
            self.intensity = intensities
            num_points = len(intensities)
            
            # Generate 2theta array based on typical XRD range
            if num_points > 1:
                step = (end_angle - start_angle) / (num_points - 1)
                self.two_theta = [start_angle + i * step for i in range(num_points)]
            else:
                self.two_theta = [start_angle]
        
        # Debug: print some info about what we found
        if intensities:
            num_points = len(intensities)
            print(f"Found {num_points} data points")
            print(f"Intensity range: {min(intensities):.1f} - {max(intensities):.1f}")
            print(f"2Theta range: {min(self.two_theta):.1f} - {max(self.two_theta):.1f}")
            
            # Warn if data seems incomplete
            if num_points < 500:
                print(f"WARNING: Only {num_points} data points found in RAW file.")
                print("This RAW file may contain incomplete data or use a different format.")
                print("For complete data, try using the corresponding BRML file if available.")
        else:
            print("WARNING: No intensity data found in RAW file")
            print("This RAW file may be corrupted, empty, or use an unsupported format.")
    
    def calculate_errors(self):
        """Calculate statistical errors for intensity values."""
        if not self.intensity:
            return
        
        # Use Poisson statistics: error = sqrt(intensity)
        # With minimum error floor
        self.error = []
        for intensity in self.intensity:
            if intensity > 0:
                error = max(np.sqrt(intensity), 1.0)  # Minimum error of 1
            else:
                error = 1.0
            self.error.append(error)
    
    def write_xye_file(self, output_path):
        """Write data to XYE format file."""
        if not self.two_theta or not self.intensity:
            print("No data to write")
            return False
        
        # Ensure all arrays are same length
        min_length = min(len(self.two_theta), len(self.intensity))
        if self.error:
            min_length = min(min_length, len(self.error))
        
        self.two_theta = self.two_theta[:min_length]
        self.intensity = self.intensity[:min_length]
        
        if not self.error:
            self.calculate_errors()
        self.error = self.error[:min_length]
        
        try:
            with open(output_path, 'w') as f:
                f.write("# Two-Theta Intensity Error\n")
                for i in range(min_length):
                    f.write(f"{self.two_theta[i]:.6f} {self.intensity[i]:.6f} {self.error[i]:.6f}\n")
            
            print(f"Wrote XYE file: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error writing XYE file: {e}")
            return False
    
    def write_metadata_file(self, output_path):
        """Write metadata to separate file."""
        try:
            with open(output_path, 'w') as f:
                f.write("# XRD File Metadata\n")
                f.write("# Extracted from source file\n\n")
                
                for key, value in sorted(self.metadata.items()):
                    f.write(f"{key}: {value}\n")
                
                if self.two_theta and self.intensity:
                    f.write(f"\n# Data Summary\n")
                    f.write(f"DATA_POINTS: {len(self.intensity)}\n")
                    f.write(f"TWO_THETA_RANGE: {min(self.two_theta):.3f} - {max(self.two_theta):.3f}\n")
                    f.write(f"INTENSITY_RANGE: {min(self.intensity):.3f} - {max(self.intensity):.3f}\n")
            
            print(f"Wrote metadata file: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error writing metadata file: {e}")
            return False
    
    def convert_file(self, input_path):
        """Convert a single file from BRML/RAW to XYE format."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"File not found: {input_path}")
            return False
        
        # Determine file type and read
        success = False
        if input_path.suffix.lower() == '.brml':
            success = self.read_brml_file(input_path)
        elif input_path.suffix.lower() == '.raw':
            success = self.read_raw_file(input_path)
        else:
            print(f"Unsupported file type: {input_path.suffix}")
            return False
        
        if not success:
            return False
        
        # Generate output filenames
        base_name = input_path.stem
        output_dir = input_path.parent
        
        xye_path = output_dir / f"{base_name}.xye"
        metadata_path = output_dir / f"{base_name}.metadata"
        
        # Write output files
        xye_success = self.write_xye_file(xye_path)
        metadata_success = self.write_metadata_file(metadata_path)
        
        return xye_success and metadata_success


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Convert BRML/RAW XRD files to XYE format')
    parser.add_argument('files', nargs='+', help='Input BRML or RAW files to convert')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    for filepath in args.files:
        if args.verbose:
            print(f"Converting: {filepath}")
        
        converter = XRDConverter()
        success = converter.convert_file(filepath)
        
        if success:
            print(f"Successfully converted: {filepath}")
        else:
            print(f"Failed to convert: {filepath}")


if __name__ == "__main__":
    main()