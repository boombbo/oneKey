# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['oneKey.py'],
    pathex=[],
    binaries=[],
    datas=[('ClearBrowsingHistory.bat', '.'), 
    ('ClearBrowsingHistory.ps1', '.'),
    ('data/*', 'data'),  # Note: The '/*' is used to include all files inside the directory
    ('README.MD', '.')], 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='oneKeyComplete',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
