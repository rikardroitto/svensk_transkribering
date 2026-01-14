# Guide: Windows Standalone-applikation med CUDA

Detta dokument beskriver hur du skapar en fristående Windows-applikation av Whisper Diarize med CUDA-stöd.

## Översikt

För att skapa en standalone Windows-app behöver vi:
1. **Packa Python-appen** med PyInstaller
2. **Bundla CUDA runtime** (inte drivers)
3. **Skapa en installer** med NSIS eller Inno Setup
4. **Auto-detect CUDA** och fallback till CPU

## Utmaningar

- **Stor storlek**: PyTorch + CUDA är ~2-3 GB
- **GPU drivers**: Användare måste ha NVIDIA drivers installerade
- **Model download**: Första körningen laddar ner modeller (~1.5GB)
- **FFmpeg**: Behövs för ljudbearbetning

---

## Metod 1: PyInstaller + NSIS Installer (Bäst för distribution)

### Steg 1: Förbered miljön på Windows

```bash
# På Windows-maskinen
python -m venv venv_windows
venv_windows\Scripts\activate

# Installera dependencies
pip install -r whisper_diarize\requirements.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Installera PyInstaller
pip install pyinstaller
```

### Steg 2: Skapa PyInstaller spec-fil

Skapa `whisper_diarize.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Samla alla dependencies
hiddenimports = [
    'torch',
    'torchaudio',
    'whisper',
    'pyannote.audio',
    'flask',
    'soundfile',
    'numpy',
    'scipy',
    'sklearn',
]

# Lägg till alla torch submoduler
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('torchaudio')
hiddenimports += collect_submodules('pyannote')

# Samla data-filer
datas = []
datas += collect_data_files('torch')
datas += collect_data_files('torchaudio')
datas += collect_data_files('pyannote.audio')

# Lägg till CUDA libraries från venv
cuda_libs = [
    ('venv_windows/Lib/site-packages/nvidia/cudnn/bin', 'nvidia/cudnn/bin'),
    ('venv_windows/Lib/site-packages/nvidia/cublas/bin', 'nvidia/cublas/bin'),
    ('venv_windows/Lib/site-packages/nvidia/cuda_runtime/bin', 'nvidia/cuda_runtime/bin'),
]
datas += cuda_libs

a = Analysis(
    ['launcher.py'],  # Se nedan för launcher-script
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
    [],
    exclude_binaries=True,
    name='WhisperDiarize',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sätt till True för debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Lägg till din icon
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
```

### Steg 3: Skapa launcher-script

Skapa `launcher.py`:

```python
"""
Windows Launcher för Whisper Diarize
Startar Flask-servern och öppnar webbläsaren automatiskt
"""
import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

# Konfigurera miljövariabler före import
def setup_environment():
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)

        # Sätt CUDA library paths
        cuda_paths = [
            base_path / "nvidia" / "cudnn" / "bin",
            base_path / "nvidia" / "cublas" / "bin",
            base_path / "nvidia" / "cuda_runtime" / "bin",
        ]

        path_str = os.environ.get("PATH", "")
        for cuda_path in cuda_paths:
            if cuda_path.exists():
                path_str = str(cuda_path) + os.pathsep + path_str

        os.environ["PATH"] = path_str

        # Sätt output directory till användarmapp
        user_dir = Path.home() / "WhisperDiarize"
        user_dir.mkdir(exist_ok=True)
        os.environ["WD_OUTPUT_DIR"] = str(user_dir)

        print(f"Output directory: {user_dir}")

    # Disable symlinks för HuggingFace
    os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

setup_environment()

# Nu kan vi importera Flask-appen
from whisper_diarize.webapp import run

def open_browser():
    """Öppna webbläsaren efter en kort fördröjning"""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("=" * 60)
    print("Whisper Diarize - Lokal transkribering och diarisering")
    print("=" * 60)
    print()
    print("Startar server på http://127.0.0.1:5000")
    print("Webbläsaren öppnas automatiskt...")
    print()

    # Öppna browser i bakgrund
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Starta Flask
    try:
        run(host="127.0.0.1", port=5000)
    except KeyboardInterrupt:
        print("\nServern stoppades av användaren")
    except Exception as e:
        print(f"\nFel: {e}")
        input("Tryck Enter för att avsluta...")
```

### Steg 4: Bygg executable

```bash
# På Windows
pyinstaller whisper_diarize.spec

# Detta skapar dist/WhisperDiarize/ mappen med alla filer
```

### Steg 5: Skapa NSIS Installer

Skapa `installer.nsi`:

```nsis
; Whisper Diarize Installer Script
!include "MUI2.nsh"

Name "Whisper Diarize"
OutFile "WhisperDiarizeSetup.exe"
InstallDir "$PROGRAMFILES64\WhisperDiarize"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Swedish"
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"

    ; Kopiera alla filer från dist/WhisperDiarize
    File /r "dist\WhisperDiarize\*.*"

    ; Skapa genvägar
    CreateDirectory "$SMPROGRAMS\Whisper Diarize"
    CreateShortCut "$SMPROGRAMS\Whisper Diarize\Whisper Diarize.lnk" "$INSTDIR\WhisperDiarize.exe"
    CreateShortCut "$DESKTOP\Whisper Diarize.lnk" "$INSTDIR\WhisperDiarize.exe"

    ; Registrera uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    CreateShortCut "$SMPROGRAMS\Whisper Diarize\Avinstallera.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\Whisper Diarize\*.*"
    RMDir "$SMPROGRAMS\Whisper Diarize"
    Delete "$DESKTOP\Whisper Diarize.lnk"
SectionEnd
```

Bygg installer:
```bash
makensis installer.nsi
```

---

## Metod 2: Electron Desktop App (Bättre UI)

Fördelar:
- Native desktop-känsla
- Bättre UI-kontroll
- Enklare att distribuera

### Struktur:

```
whisper-diarize-app/
├── electron/
│   ├── main.js          # Electron main process
│   ├── preload.js
│   └── package.json
├── whisper_diarize/     # Din Python-kod
└── python_server.py     # Flask-server wrapper
```

### electron/main.js:

```javascript
const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess = null;
let mainWindow = null;

function startFlaskServer() {
    // Hitta python executable i packaged app
    const pythonPath = app.isPackaged
        ? path.join(process.resourcesPath, 'python', 'python.exe')
        : 'python';

    const serverScript = app.isPackaged
        ? path.join(process.resourcesPath, 'server', 'python_server.py')
        : path.join(__dirname, '..', 'python_server.py');

    flaskProcess = spawn(pythonPath, [serverScript]);

    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'icon.ico')
    });

    // Vänta tills Flask är redo
    setTimeout(() => {
        mainWindow.loadURL('http://127.0.0.1:5000');
    }, 3000);
}

app.whenReady().then(() => {
    startFlaskServer();
    createWindow();
});

app.on('window-all-closed', () => {
    if (flaskProcess) {
        flaskProcess.kill();
    }
    app.quit();
});
```

Bygg med electron-builder:
```bash
npm install electron electron-builder
npm run build  # Skapar Windows .exe
```

---

## Metod 3: Docker Desktop för Windows (Enklast för CUDA)

### docker-compose.yml:

```yaml
version: '3.8'
services:
  whisper-diarize:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Dockerfile:

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY whisper_diarize ./whisper_diarize
COPY requirements.txt .

RUN pip3 install -r requirements.txt
RUN pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

EXPOSE 5000
CMD ["python3", "-m", "whisper_diarize.webapp"]
```

Användning på Windows:
1. Installera Docker Desktop med WSL2
2. Aktivera NVIDIA Container Toolkit
3. Kör: `docker-compose up`
4. Öppna http://localhost:5000

---

## System Requirements för Standalone-app

### Minimum:
- Windows 10/11 64-bit
- 8GB RAM (16GB rekommenderat)
- 10GB disk space
- NVIDIA GPU med CUDA Compute Capability 6.0+ (för GPU-acceleration)
- NVIDIA Driver 525.60.13 eller nyare

### Optional (för CPU-only):
- Samma som ovan men utan GPU-krav
- Längre bearbetningstid (5-10x långsammare)

---

## Auto-detect CUDA och Fallback

I din `utils.py`, förbättra `get_optimal_device()`:

```python
def get_optimal_device() -> Tuple[str, str]:
    """
    Detektera bästa device med tydliga användarmeddeland.
    """
    import torch

    if not torch.cuda.is_available():
        print("=" * 60)
        print("⚠️  CUDA inte tillgänglig")
        print("    Använder CPU-läge (långsammare)")
        print("    För GPU-acceleration:")
        print("    1. Installera NVIDIA GPU drivers")
        print("    2. Se till att du har en CUDA-kompatibel GPU")
        print("=" * 60)
        return "cpu", "int8"

    try:
        # Test CUDA functionality
        test_tensor = torch.zeros(1).cuda()
        del test_tensor
        torch.cuda.empty_cache()

        gpu_name = torch.cuda.get_device_name(0)
        print("=" * 60)
        print(f"✓ GPU detekterad: {gpu_name}")
        print(f"   CUDA Version: {torch.version.cuda}")
        print("   Använder GPU-acceleration")
        print("=" * 60)
        return "cuda", "float16"

    except Exception as e:
        print("=" * 60)
        print(f"⚠️  CUDA tillgänglig men ej funktionell: {e}")
        print("    Faller tillbaka på CPU-läge")
        print("=" * 60)
        return "cpu", "int8"
```

---

## Distribution Checklist

### För PyInstaller-versionen:

- [ ] Testa på ren Windows-maskin utan Python installerat
- [ ] Verifiera att CUDA fungerar med GPU
- [ ] Verifiera att CPU-fallback fungerar utan GPU
- [ ] Testa med olika ljudformat (MP3, WAV, M4A)
- [ ] Kontrollera att modeller laddas ner korrekt första gången
- [ ] Testa HF_TOKEN-konfiguration
- [ ] Verifiera att output-filer sparas rätt
- [ ] Lägg till README med systemkrav
- [ ] Skapa user guide på svenska

### För Electron-versionen:

- [ ] Alla punkter ovan
- [ ] Testa window management (minimize, maximize, close)
- [ ] Verifiera att Flask-servern stoppas när appen stängs
- [ ] Testa file picker för upload
- [ ] Auto-updater funktionalitet

---

## Rekommendation

**För enkel distribution**: Använd **Metod 1 (PyInstaller + NSIS)**
- Enklast att underhålla
- Minsta storlek (~2.5GB komprimerat installer)
- Fungerar offline efter initial model-download

**För bättre UX**: Använd **Metod 2 (Electron)**
- Native desktop-känsla
- Enklare att lägga till features (drag-drop, system tray, etc.)
- Automatiska uppdateringar med electron-updater

**För utveckling/power users**: Använd **Metod 3 (Docker)**
- Enklast CUDA-setup
- Konsekvent miljö
- Kräver Docker Desktop

## Nästa steg

1. Välj approach baserat på målgrupp
2. Skapa test-build på Windows-maskin
3. Testa på ren Windows-installation
4. Skapa installer
5. Dokumentera systemkrav och setup
6. Överväg code-signing för Windows SmartScreen
