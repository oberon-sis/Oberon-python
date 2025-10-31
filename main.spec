# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# 1. COLETA DE DEPENDÊNCIAS
# Colete tudo do mysql.connector para resolver warnings/erros de importação
datas_mysql, binaries_mysql, hiddenimports_mysql = collect_all('mysql.connector')

icone_path = 'app_icon.ico' 

# Adiciona a DLL do runtime C++ no Windows (necessário para alguns binários)
binaries_list = []
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
    
    # Junta os binários coletados do MySQL e os binários adicionais
    binaries=binaries_mysql + binaries_list, 
    
    # Junta as datas coletadas do MySQL com os arquivos do projeto
    datas=datas_mysql + [
        ('OBERON_ENV.example', '.'), 
        ('src', 'src'),
        ('utils', 'utils'),
    ],
    
    # 2. CORREÇÃO DE IMPORTS OCULTOS:
    # Inclui dependências problemáticas como psutil, python-dotenv e o 'encodings'
    hiddenimports=hiddenimports_mysql + [
        'psutil',
        'python-dotenv',
        'encodings', # 🌟 CORREÇÃO PARA ModuleNotFoundError: No module named 'encodings'
        'io' 
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

pyz = PYZ(a.pure, 
          a.zipped_data,
          cipher=None,
          )

# 3. CRIAÇÃO DO EXECUTÁVEL (ONEFILE)
# A ausência do bloco COLLECT força a criação de um executável de arquivo único
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Inclui os binários na execução
    a.zipfiles,  # Inclui os arquivos compactados
    a.datas,     # Inclui os arquivos de dados (como .env)
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

# 🛑 O BLOCO COLLECT DEVE SER REMOVIDO PARA CRIAR UM EXECUTÁVEL SINGLE-FILE.
# coll = COLLECT(...)