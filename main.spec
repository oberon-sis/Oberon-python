# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[], 
    
    binaries=[],
    
    datas=[
        ('OBERON_ENV.example', '.'), 
        
        ('src', 'src'),
        ('utils', 'utils'),
        
    ],
    
    hiddenimports=[], 
    
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
          # name='PYZ-00.pyz', # Descomente se precisar de nome específico
          )

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OberonAgente', # Define o nome final do executável (sem extensão)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Mantenha como True se for um aplicativo de linha de comando/terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
