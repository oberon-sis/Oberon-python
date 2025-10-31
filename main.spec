# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import sys
import os

icone_path = 'app_icon.ico' 

try:
    mysql_path = os.path.dirname(sys.modules['mysql.connector'].__file__)
except:
    mysql_path = None

binaries_list = []
if mysql_path:
    binaries_list.append((mysql_path, 'mysql.connector'))

try:
    runtime_dll_path = os.path.join(sys.exec_prefix, 'DLLs', 'vcruntime140.dll')
    if os.path.exists(runtime_dll_path):
        binaries_list.append((runtime_dll_path, '.'))
except:
    pass
    
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[], 
    
    binaries=binaries_list, # Usa a lista de binários coletada
    
    datas=[
        ('OBERON_ENV.example', '.'), 
        
        ('src', 'src'),
        ('utils', 'utils'),
        
    ],
    
    # 🌟 ADICIONANDO IMPORTAÇÕES OCULTAS (REFORÇANDO TODAS AS BIBLIOTECAS)
    hiddenimports=[
        'mysql.connector', 
        'mysql.connector.locales.en',
        'psutil',       
        'python-dotenv' 
    ], 
    
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    
    excludes=[
        'tkinter', 
        'unittest', 
        'pydoc',
        'doctest',
        'setuptools'
    ],
    
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=None,
          )

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OberonAgente', 
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
    icon=icone_path 
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OberonAgente',
)
