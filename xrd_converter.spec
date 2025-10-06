# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

a = Analysis(
    ['xrd_converter_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'xml.etree.ElementTree',
        'zipfile',
        'struct',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'threading',
        'pathlib',
        'platform',
        'urllib.parse'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='XRD_Format_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='XRD Format Converter.app',
        icon=None,
        bundle_identifier='edu.csu.xrd.converter',
        version='1.0.0',
        info_plist={
            'CFBundleName': 'XRD Format Converter',
            'CFBundleDisplayName': 'XRD Format Converter', 
            'CFBundleGetInfoString': 'Converting BRML/RAW files to XYE format',
            'CFBundleIdentifier': 'edu.csu.xrd.converter',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': 'Copyright © 2024, Colorado State University',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'BRML files',
                    'LSItemContentTypes': ['public.data'],
                    'CFBundleTypeRole': 'Viewer',
                    'CFBundleTypeExtensions': ['brml'],
                },
                {
                    'CFBundleTypeName': 'RAW files',
                    'LSItemContentTypes': ['public.data'], 
                    'CFBundleTypeRole': 'Viewer',
                    'CFBundleTypeExtensions': ['raw'],
                }
            ]
        }
    )