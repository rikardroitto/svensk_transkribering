# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec-fil för Whisper Diarize Windows-applikation

Användning:
    1. Installera PyInstaller: pip install pyinstaller
    2. Bygg: pyinstaller whisper_diarize_windows.spec
    3. Hittar executable i: dist/WhisperDiarize/WhisperDiarize.exe

OBS: Detta måste köras på en Windows-maskin med alla dependencies installerade!
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Hitta alla nödvändiga submoduler
hiddenimports = [
    # Core dependencies
    'torch',
    'torchaudio',
    'faster_whisper',
    'pyannote.audio',
    'pyannote.core',
    'pyannote.database',
    'pyannote.metrics',
    'pyannote.pipeline',

    # Flask och webb
    'flask',
    'werkzeug',
    'jinja2',
    'click',

    # Audio och ML
    'soundfile',
    'numpy',
    'scipy',
    'sklearn',
    'pandas',
    'tqdm',
    'librosa',

    # Utilities
    'dotenv',
    'pydub',
    'huggingface_hub',
    'tokenizers',
    'yaml',

    # CUDA support
    'nvidia.cudnn',
    'nvidia.cublas',
    'nvidia.cuda_runtime',
]

# Samla alla torch och pyannote submoduler
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('torchaudio')
hiddenimports += collect_submodules('pyannote')
hiddenimports += collect_submodules('faster_whisper')

# Samla data-filer från packages
datas = []
datas += collect_data_files('torch', include_py_files=False)
datas += collect_data_files('torchaudio', include_py_files=False)
datas += collect_data_files('pyannote', include_py_files=False)
datas += collect_data_files('faster_whisper', include_py_files=False)

# Lägg till applikationens egna filer
datas += [
    ('whisper_diarize', 'whisper_diarize'),
    ('.env.example', '.'),
    ('ANVANDARE_README.txt', '.'),  # Användarguide för Windows-användare
]

# VIKTIGT: Lägg till CUDA libraries från venv (justera sökväg efter behov)
# OBS: Detta förutsätter att du kör från projektets root och har en venv
venv_path = 'venv/Lib/site-packages'  # Alternativt: '.venv/Lib/site-packages'

cuda_libs = [
    (f'{venv_path}/nvidia/cudnn/bin', 'nvidia/cudnn/bin'),
    (f'{venv_path}/nvidia/cublas/bin', 'nvidia/cublas/bin'),
    (f'{venv_path}/nvidia/cuda_runtime/bin', 'nvidia/cuda_runtime/bin'),

    # Lägg även till lib-mapparna för säkerhetsskull
    (f'{venv_path}/nvidia/cudnn/lib', 'nvidia/cudnn/lib'),
    (f'{venv_path}/nvidia/cublas/lib', 'nvidia/cublas/lib'),
    (f'{venv_path}/nvidia/cuda_runtime/lib', 'nvidia/cuda_runtime/lib'),
]

# Kontrollera om CUDA libraries finns innan vi lägger till dem
for src, dst in cuda_libs:
    if os.path.exists(src):
        datas.append((src, dst))
        print(f"✓ Lade till CUDA library: {src}")
    else:
        print(f"⚠️  CUDA library saknas: {src}")

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exkludera onödiga packages för att minska storlek
        'matplotlib',  # Om du inte behöver plotting
        'IPython',
        'notebook',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhisperDiarize',
    debug=False,  # Sätt till True för debug output
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Sätt till False för GUI-läge (ingen console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperDiarize',
)
