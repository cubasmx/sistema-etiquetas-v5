# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PythonApplication1.py'],
    pathex=[],
    binaries=[],
    datas=[('styles.qss', '.'), ('odoo_config.py', '.'), ('config.json', '.'), ('printer_config.json', '.'), ('src', 'src'), ('src/ui/icons', 'src/ui/icons'), ('src/assets', 'src/assets')],
    hiddenimports=['mysql.connector', 'mysql', 'odoorpc', 'odoo_client', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sistema-etiquetas',
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
    icon=['src\\assets\\icon.ico'],
)
