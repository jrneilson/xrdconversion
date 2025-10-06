#!/usr/bin/env python3
"""
Setup script for building XRD Format Converter executables
Supports both PyInstaller (cross-platform) and py2app (macOS)
"""

import sys
import os
from setuptools import setup

APP = ['xrd_converter_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'XRD Format Converter',
        'CFBundleDisplayName': 'XRD Format Converter',
        'CFBundleGetInfoString': "Converting BRML/RAW files to XYE format",
        'CFBundleIdentifier': "edu.csu.xrd.converter",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, Colorado State University",
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'BRML files',
                'CFBundleTypeIconFile': None,
                'LSItemContentTypes': ['public.data'],
                'CFBundleTypeRole': 'Viewer',
                'CFBundleTypeExtensions': ['brml'],
            },
            {
                'CFBundleTypeName': 'RAW files', 
                'CFBundleTypeIconFile': None,
                'LSItemContentTypes': ['public.data'],
                'CFBundleTypeRole': 'Viewer',
                'CFBundleTypeExtensions': ['raw'],
            }
        ]
    }
}

if sys.platform == 'darwin':
    # macOS build with py2app
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
        install_requires=[
            'tkinter',
            'numpy',
            'matplotlib'
        ]
    )
else:
    # Standard setuptools for other platforms
    setup(
        name='XRD Format Converter',
        version='1.0.0',
        description='Convert BRML/RAW files to XYE format',
        author='Colorado State University',
        py_modules=['xrd_converter', 'xrd_converter_gui'],
        install_requires=[
            'tkinter',
            'numpy', 
            'matplotlib'
        ],
        entry_points={
            'console_scripts': [
                'xrd-converter=xrd_converter_gui:main',
            ],
        }
    )