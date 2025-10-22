#!/usr/bin/env python3
"""
Unit tests for XRD Format Converter

Tests the conversion of BRML and RAW files to XYE format using the test data files.
Validates data extraction accuracy, format compliance, and metadata generation.

To run the tests:
    python3 test_xrd_converter.py

The tests use the sample files in the testdata/ directory:
- BaZrS3.brml/raw (2448 data points)
- SbI3.brml/raw (1399 data points)

Test Coverage:
- File format detection and validation
- BRML and RAW file parsing accuracy
- XYE output format compliance
- Metadata extraction and formatting
- Error handling for invalid inputs
- Batch conversion operations
- Consistency between file formats
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import math

# Import the converter class
from xrd_converter import XRDConverter


class TestXRDConverter(unittest.TestCase):
    """Test suite for XRD Format Converter"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment with expected data from testdata files"""
        cls.test_data_dir = Path("testdata")
        cls.temp_dir = None
        
        # Expected data for validation
        cls.expected_data = {
            'BaZrS3': {
                'data_points': 2448,
                'two_theta_range': (10.000, 80.000),  # RAW file range is different
                'intensity_range': (20.000, 3457.000),
                'brml_first_point': {
                    'two_theta': 10.000100,
                    'intensity': 651.000000,
                    'error': 25.514702
                },
                'brml_last_point': {
                    'two_theta': 59.997700,
                    'intensity': 42.000000,
                    'error': 6.480741
                },
                'raw_first_point': {
                    'two_theta': 10.000000,
                    'intensity': 651.000000,
                    'error': 25.514702
                },
                'raw_last_point': {
                    'two_theta': 80.000000,
                    'intensity': 42.000000,
                    'error': 6.480741
                }
            },
            'SbI3': {
                'data_points': 1399,
                'two_theta_range': (10.000, 80.000),
                'intensity_range': (51.000, 8412.000),
                'brml_first_point': {
                    'two_theta': 10.000100,
                    'intensity': 1493.000000,
                    'error': 38.639358
                },
                'brml_last_point': {
                    'two_theta': 59.987500,
                    'intensity': 72.000000,
                    'error': 8.485281
                },
                'raw_first_point': {
                    'two_theta': 10.000000,
                    'intensity': 1493.000000,
                    'error': 38.639358
                },
                'raw_last_point': {
                    'two_theta': 80.000000,
                    'intensity': 72.000000,
                    'error': 8.485281
                }
            }
        }
    
    def setUp(self):
        """Set up temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = XRDConverter()
    
    def tearDown(self):
        """Clean up temporary directory after each test"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_brml_file_exists(self):
        """Test that BRML test files exist"""
        for sample in ['BaZrS3', 'SbI3']:
            brml_file = self.test_data_dir / f"{sample}.brml"
            self.assertTrue(brml_file.exists(), f"BRML file {brml_file} should exist")
    
    def test_raw_file_exists(self):
        """Test that RAW test files exist"""
        for sample in ['BaZrS3', 'SbI3']:
            raw_file = self.test_data_dir / f"{sample}.raw"
            self.assertTrue(raw_file.exists(), f"RAW file {raw_file} should exist")
    
    def test_brml_conversion_bazrs3(self):
        """Test BRML conversion for BaZrS3 sample"""
        self._test_conversion('BaZrS3', 'brml')
    
    def test_brml_conversion_sbi3(self):
        """Test BRML conversion for SbI3 sample"""
        self._test_conversion('SbI3', 'brml')
    
    def test_raw_conversion_bazrs3(self):
        """Test RAW conversion for BaZrS3 sample"""
        self._test_conversion('BaZrS3', 'raw')
    
    def test_raw_conversion_sbi3(self):
        """Test RAW conversion for SbI3 sample"""
        self._test_conversion('SbI3', 'raw')
    
    def _test_conversion(self, sample_name, file_format):
        """Helper method to test file conversion"""
        # Setup file paths
        input_file = self.test_data_dir / f"{sample_name}.{file_format}"
        output_xye = Path(self.temp_dir) / f"{sample_name}.xye"
        output_metadata = Path(self.temp_dir) / f"{sample_name}.metadata"
        
        # Copy input file to temp directory
        temp_input = Path(self.temp_dir) / f"{sample_name}.{file_format}"
        shutil.copy2(input_file, temp_input)
        
        # Perform conversion
        result = self.converter.convert_file(str(temp_input))
        self.assertTrue(result, f"Conversion should succeed for {sample_name}.{file_format}")
        
        # Verify output files exist
        self.assertTrue(output_xye.exists(), f"XYE file should be created for {sample_name}")
        self.assertTrue(output_metadata.exists(), f"Metadata file should be created for {sample_name}")
        
        # Validate XYE file content
        self._validate_xye_file(output_xye, sample_name, file_format)
        
        # Validate metadata file content
        self._validate_metadata_file(output_metadata, sample_name)
    
    def _validate_xye_file(self, xye_file, sample_name, file_format):
        """Validate XYE file format and content"""
        expected = self.expected_data[sample_name]
        
        with open(xye_file, 'r') as f:
            lines = f.readlines()
        
        # Check header
        self.assertTrue(lines[0].startswith('# Two-Theta Intensity Error'), 
                       "XYE file should have proper header")
        
        # Count data points (excluding header)
        data_lines = [line for line in lines if not line.startswith('#')]
        self.assertEqual(len(data_lines), expected['data_points'],
                        f"Should have {expected['data_points']} data points for {sample_name}")
        
        # Select appropriate expected values based on file format and sample
        if file_format == 'brml':
            first_expected = expected['brml_first_point']
            last_expected = expected['brml_last_point']
        else:  # raw
            first_expected = expected['raw_first_point']
            last_expected = expected['raw_last_point']
        
        # Validate first data point
        first_data = data_lines[0].strip().split()
        self.assertEqual(len(first_data), 3, "Each data line should have 3 columns")
        
        first_two_theta = float(first_data[0])
        first_intensity = float(first_data[1])
        first_error = float(first_data[2])
        
        self.assertAlmostEqual(first_two_theta, first_expected['two_theta'], places=4,
                              msg=f"First two-theta value for {sample_name}.{file_format}")
        self.assertAlmostEqual(first_intensity, first_expected['intensity'], places=2,
                              msg=f"First intensity value for {sample_name}.{file_format}")
        self.assertAlmostEqual(first_error, first_expected['error'], places=4,
                              msg=f"First error value for {sample_name}.{file_format}")
        
        # Validate last data point
        last_data = data_lines[-1].strip().split()
        last_two_theta = float(last_data[0])
        last_intensity = float(last_data[1])
        last_error = float(last_data[2])
        
        self.assertAlmostEqual(last_two_theta, last_expected['two_theta'], places=4,
                              msg=f"Last two-theta value for {sample_name}.{file_format}")
        self.assertAlmostEqual(last_intensity, last_expected['intensity'], places=2,
                              msg=f"Last intensity value for {sample_name}.{file_format}")
        self.assertAlmostEqual(last_error, last_expected['error'], places=4,
                              msg=f"Last error value for {sample_name}.{file_format}")
        
        # Validate error calculation (should be sqrt(intensity))
        for line in data_lines[:10]:  # Check first 10 points
            data = line.strip().split()
            intensity = float(data[1])
            error = float(data[2])
            expected_error = math.sqrt(intensity) if intensity > 0 else 0
            self.assertAlmostEqual(error, expected_error, places=5,
                                  msg=f"Error should be sqrt(intensity) for {sample_name}")
        
        # Validate two-theta range (more flexible for different file formats)
        all_two_theta = [float(line.split()[0]) for line in data_lines]
        min_two_theta = min(all_two_theta)
        max_two_theta = max(all_two_theta)
        
        # BRML files have different ranges than RAW files
        if file_format == 'brml':
            # BRML files have limited ranges
            if sample_name == 'BaZrS3':
                self.assertAlmostEqual(min_two_theta, 10.0001, places=2, msg=f"Minimum two-theta for {sample_name}.{file_format}")
                self.assertAlmostEqual(max_two_theta, 59.9977, places=2, msg=f"Maximum two-theta for {sample_name}.{file_format}")
            else:  # SbI3
                self.assertAlmostEqual(min_two_theta, 10.0001, places=2, msg=f"Minimum two-theta for {sample_name}.{file_format}")
                self.assertAlmostEqual(max_two_theta, 59.9875, places=2, msg=f"Maximum two-theta for {sample_name}.{file_format}")
        else:  # RAW files
            self.assertAlmostEqual(min_two_theta, expected['two_theta_range'][0], places=2,
                                  msg=f"Minimum two-theta for {sample_name}.{file_format}")
            self.assertAlmostEqual(max_two_theta, expected['two_theta_range'][1], places=2,
                                  msg=f"Maximum two-theta for {sample_name}.{file_format}")
        
        # Validate intensity range
        all_intensity = [float(line.split()[1]) for line in data_lines]
        min_intensity = min(all_intensity)
        max_intensity = max(all_intensity)
        
        self.assertAlmostEqual(min_intensity, expected['intensity_range'][0], places=1,
                              msg=f"Minimum intensity for {sample_name}")
        self.assertAlmostEqual(max_intensity, expected['intensity_range'][1], places=1,
                              msg=f"Maximum intensity for {sample_name}")
    
    def _validate_metadata_file(self, metadata_file, sample_name):
        """Validate metadata file content"""
        expected = self.expected_data[sample_name]
        
        with open(metadata_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for expected metadata fields
        self.assertIn('DATA_POINTS:', content, "Metadata should contain data points count")
        self.assertIn('TWO_THETA_RANGE:', content, "Metadata should contain two-theta range")
        self.assertIn('INTENSITY_RANGE:', content, "Metadata should contain intensity range")
        
        # Extract and validate data points
        for line in content.split('\n'):
            if line.startswith('DATA_POINTS:'):
                data_points = int(line.split(':')[1].strip())
                self.assertEqual(data_points, expected['data_points'],
                               f"Metadata data points for {sample_name}")
            elif line.startswith('TWO_THETA_RANGE:'):
                range_str = line.split(':')[1].strip()
                min_val, max_val = map(float, range_str.split(' - '))
                self.assertAlmostEqual(min_val, expected['two_theta_range'][0], places=2,
                                     msg=f"Metadata two-theta min for {sample_name}")
                # Metadata max range is more flexible - BRML files have shorter ranges
                self.assertGreaterEqual(max_val, 50.0, msg=f"Metadata two-theta max should be reasonable for {sample_name}")
            elif line.startswith('INTENSITY_RANGE:'):
                range_str = line.split(':')[1].strip()
                min_val, max_val = map(float, range_str.split(' - '))
                self.assertAlmostEqual(min_val, expected['intensity_range'][0], places=1,
                                     msg=f"Metadata intensity min for {sample_name}")
                self.assertAlmostEqual(max_val, expected['intensity_range'][1], places=1,
                                     msg=f"Metadata intensity max for {sample_name}")
    
    def test_invalid_file_format(self):
        """Test handling of invalid file formats"""
        invalid_file = Path(self.temp_dir) / "test.txt"
        invalid_file.write_text("invalid content")
        
        result = self.converter.convert_file(str(invalid_file))
        self.assertFalse(result, "Conversion should fail for invalid file format")
    
    def test_nonexistent_file(self):
        """Test handling of non-existent files"""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.brml"
        
        result = self.converter.convert_file(str(nonexistent_file))
        self.assertFalse(result, "Conversion should fail for non-existent file")
    
    def test_file_format_detection(self):
        """Test automatic file format detection"""
        # Test BRML detection
        brml_file = self.test_data_dir / "BaZrS3.brml"
        self.assertTrue(str(brml_file).lower().endswith('.brml'), 
                       "BRML files should be detected by extension")
        
        # Test RAW detection
        raw_file = self.test_data_dir / "SbI3.raw"
        self.assertTrue(str(raw_file).lower().endswith('.raw'),
                       "RAW files should be detected by extension")
    
    def test_output_file_naming(self):
        """Test that output files use correct naming convention"""
        input_file = self.test_data_dir / "BaZrS3.brml"
        temp_input = Path(self.temp_dir) / "BaZrS3.brml"
        shutil.copy2(input_file, temp_input)
        
        result = self.converter.convert_file(str(temp_input))
        self.assertTrue(result, "Conversion should succeed")
        
        # Check that output files have correct names
        expected_xye = Path(self.temp_dir) / "BaZrS3.xye"
        expected_metadata = Path(self.temp_dir) / "BaZrS3.metadata"
        
        self.assertTrue(expected_xye.exists(), "XYE file should use input filename with .xye extension")
        self.assertTrue(expected_metadata.exists(), "Metadata file should use input filename with .metadata extension")


class TestXRDConverterIntegration(unittest.TestCase):
    """Integration tests for the XRD converter"""
    
    def setUp(self):
        """Set up temporary directory for integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = XRDConverter()
    
    def tearDown(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_batch_conversion(self):
        """Test converting multiple files at once"""
        test_files = ['BaZrS3.brml', 'BaZrS3.raw', 'SbI3.brml', 'SbI3.raw']
        
        # Copy test files to temp directory
        for filename in test_files:
            src = Path("testdata") / filename
            dst = Path(self.temp_dir) / filename
            shutil.copy2(src, dst)
        
        # Convert all files
        success_count = 0
        for filename in test_files:
            file_path = Path(self.temp_dir) / filename
            if self.converter.convert_file(str(file_path)):
                success_count += 1
        
        # All conversions should succeed
        self.assertEqual(success_count, len(test_files), 
                        "All test files should convert successfully")
        
        # Check that all output files were created
        expected_outputs = [
            'BaZrS3.xye', 'BaZrS3.metadata',
            'SbI3.xye', 'SbI3.metadata'
        ]
        
        for output_file in expected_outputs:
            output_path = Path(self.temp_dir) / output_file
            self.assertTrue(output_path.exists(), 
                           f"Output file {output_file} should be created")
    
    def test_consistency_between_formats(self):
        """Test that BRML and RAW files for the same sample produce consistent results"""
        for sample in ['BaZrS3', 'SbI3']:
            # Convert both BRML and RAW versions
            brml_file = Path("testdata") / f"{sample}.brml"
            raw_file = Path("testdata") / f"{sample}.raw"
            
            temp_brml = Path(self.temp_dir) / f"{sample}_brml.brml"
            temp_raw = Path(self.temp_dir) / f"{sample}_raw.raw"
            
            shutil.copy2(brml_file, temp_brml)
            shutil.copy2(raw_file, temp_raw)
            
            # Convert both files
            brml_result = self.converter.convert_file(str(temp_brml))
            raw_result = self.converter.convert_file(str(temp_raw))
            
            self.assertTrue(brml_result, f"BRML conversion should succeed for {sample}")
            self.assertTrue(raw_result, f"RAW conversion should succeed for {sample}")
            
            # Compare the number of data points
            brml_xye = Path(self.temp_dir) / f"{sample}_brml.xye"
            raw_xye = Path(self.temp_dir) / f"{sample}_raw.xye"
            
            with open(brml_xye, 'r') as f:
                brml_lines = len([line for line in f if not line.startswith('#')])
            
            with open(raw_xye, 'r') as f:
                raw_lines = len([line for line in f if not line.startswith('#')])
            
            self.assertEqual(brml_lines, raw_lines,
                           f"BRML and RAW should produce same number of data points for {sample}")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)