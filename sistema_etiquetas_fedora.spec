# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all necessary data files
datas = [
    ('styles.qss', '.'),
    ('src/assets/icon.ico', 'src/assets'),
    ('src/assets/cacert.pem', 'src/assets'),
    ('odoo_config.py', '.'),
    ('printer_config.json', '.'),
]

# Collect all necessary modules
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'xmlrpc.client',
    'pymysql',
    'socket',
    'json',
    'os',
    'sys',
    'datetime',
    'src.utils.mysql_client',
    'odoo_client',
]

a = Analysis(
    ['PythonApplication1.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='SistemaEtiquetas',
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
    icon='src/assets/icon.ico',
) 