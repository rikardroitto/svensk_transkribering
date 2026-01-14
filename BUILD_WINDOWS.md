# Snabbguide: Bygg Windows Standalone-applikation

Denna guide visar hur du snabbt bygger en körbar Windows-applikation med CUDA-stöd.

## Förberedelser (En gång)

### 1. Windows-maskin med NVIDIA GPU

Du behöver:
- Windows 10/11 64-bit
- NVIDIA GPU (för CUDA-stöd)
- NVIDIA Driver 525.60.13 eller nyare
- Python 3.12 installerat
- Git (för att klona repo)

### 2. Klona repository på Windows

```powershell
git clone <repository-url>
cd svensk_transkribering
```

### 3. Skapa och aktivera virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 4. Installera dependencies

```powershell
# Uppgradera pip
python -m pip install --upgrade pip wheel setuptools

# Installera project dependencies
pip install -r whisper_diarize\requirements.txt

# Installera PyTorch med CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Installera PyInstaller
pip install pyinstaller
```

### 5. Verifiera CUDA

```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

Du bör se:
```
CUDA: True
GPU: NVIDIA GeForce RTX [din GPU]
```

---

## Bygga Executable

### Steg 1: Testa launcher lokalt

```powershell
python launcher.py
```

Detta ska:
1. Starta Flask-servern
2. Öppna webbläsaren automatiskt
3. Visa CUDA-status

Om det fungerar, gå vidare till nästa steg.

### Steg 2: Bygg med PyInstaller

```powershell
# Bygg executable
pyinstaller whisper_diarize_windows.spec

# Detta tar 5-10 minuter och skapar:
# dist/WhisperDiarize/WhisperDiarize.exe
```

### Steg 3: Testa executable

```powershell
cd dist\WhisperDiarize
.\WhisperDiarize.exe
```

Om allt fungerar ska webbläsaren öppnas automatiskt.

---

## Felsökning

### Problem: "CUDA inte tillgänglig"

**Lösning 1**: Kontrollera att CUDA libraries kopierades
```powershell
dir dist\WhisperDiarize\nvidia
```
Du bör se mappar: `cudnn`, `cublas`, `cuda_runtime`

**Lösning 2**: Verifiera venv path i spec-filen
Öppna `whisper_diarize_windows.spec` och kontrollera:
```python
venv_path = 'venv/Lib/site-packages'  # eller '.venv/Lib/site-packages'
```

**Lösning 3**: Bygg om med verbose output
```powershell
pyinstaller --log-level DEBUG whisper_diarize_windows.spec
```

### Problem: "Module not found"

Lägg till saknad modul i spec-filen under `hiddenimports`:
```python
hiddenimports = [
    # ... befintliga imports
    'missing_module_name',
]
```

### Problem: Stor exe-storlek

Detta är normalt! PyTorch + CUDA är ~2-3 GB. För att minska:

1. **Använd UPX compression** (redan aktiverat i spec)
2. **Exkludera onödiga packages**:
   ```python
   excludes=[
       'matplotlib',
       'IPython',
       'notebook',
       'pytest',
       'tkinter',
   ]
   ```
3. **Överväg att INTE inkludera CUDA** för CPU-version

---

## Distribution

### Metod 1: Zippa mappen

```powershell
# Skapa zip
Compress-Archive -Path dist\WhisperDiarize -DestinationPath WhisperDiarize_v1.0.zip
```

Användare:
1. Unzippa
2. Dubbelklicka `WhisperDiarize.exe`

### Metod 2: Skapa installer med NSIS

Se `WINDOWS_STANDALONE.md` för detaljer om NSIS-installer.

---

## Nästa steg

### För bättre UX:

1. **Lägg till icon**:
   - Skapa eller ladda ner `icon.ico`
   - Placera i projektets root
   - Bygg om

2. **Göm console window**:
   ```python
   # I spec-filen, ändra:
   console=False,  # Istället för True
   ```

3. **Lägg till splash screen**:
   ```python
   # I spec-filen:
   splash = Splash('splash.png',
                   binaries=a.binaries,
                   datas=a.datas,
                   text_pos=(10, 50),
                   text_size=12,
                   text_color='black')
   ```

4. **Code signing** (för att undvika Windows SmartScreen):
   - Köp code signing certificate
   - Signera exe:
     ```powershell
     signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com WhisperDiarize.exe
     ```

### För enklare uppdateringar:

1. Använd **auto-updater** (kräver server för hosting)
2. Eller: Skapa **update checker** som kollar GitHub releases

---

## Systemkrav för slutanvändare

### Med GPU (rekommenderat):
- Windows 10/11 64-bit
- NVIDIA GPU med CUDA Compute Capability 6.0+
- NVIDIA Driver 525.60.13 eller nyare
- 8GB RAM (16GB rekommenderat)
- 10GB disk space

### CPU-only:
- Windows 10/11 64-bit
- 8GB RAM (16GB rekommenderat)
- 10GB disk space
- ⚠️ Mycket långsammare (5-10x)

---

## Troubleshooting för slutanvändare

### "Programmet kan inte starta eftersom..."

Installera **Microsoft Visual C++ Redistributable**:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### "Windows skyddade din dator"

Detta är Windows SmartScreen. För att köra:
1. Klicka "Mer info"
2. Klicka "Kör ändå"

För att undvika detta, signera exe med code signing certificate.

### CUDA fungerar inte

1. Kontrollera GPU driver:
   ```powershell
   nvidia-smi
   ```
2. Om ingen GPU: Appen använder CPU automatiskt (långsammare)

---

## Snabbt exempel

```powershell
# 1. Setup (en gång)
git clone <repo>
cd svensk_transkribering
python -m venv venv
.\venv\Scripts\activate
pip install -r whisper_diarize\requirements.txt
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install pyinstaller

# 2. Bygg
pyinstaller whisper_diarize_windows.spec

# 3. Testa
cd dist\WhisperDiarize
.\WhisperDiarize.exe

# 4. Distribuera
cd ..\..
Compress-Archive -Path dist\WhisperDiarize -DestinationPath WhisperDiarize.zip
```

Klart! 🎉
