# Whisper Diarize - Svensk Transkribering

Lokalt transkriberings- och diariseringssystem för svenska ljudfiler med CUDA GPU-acceleration.

## ✨ Funktioner

- 🎙️ **Transkribering**: Konvertera tal till text med Whisper (KBLab/kb-whisper-medium)
- 👥 **Diarisering**: Identifiera och separera olika talare (pyannote.audio)
- 🚀 **GPU-acceleration**: CUDA-stöd för snabb bearbetning
- 📄 **Flera format**: Export till TXT, SRT, JSON, TSV
- 🖥️ **Webb-gränssnitt**: Användarvänligt Flask-baserat UI med realtids progress
- 🔧 **CLI**: Kommandoradstöd för batch-processing

## 🚀 Snabbstart (Linux/WSL)

### 1. Aktivera miljön med CUDA-stöd

```bash
source activate_cuda.sh
```

### 2. Kör webb-gränssnittet

```bash
python -m whisper_diarize.webapp
```

Öppna webbläsaren: http://127.0.0.1:5000

### 3. Eller använd CLI

```bash
# Komplett pipeline med diarisering
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda

# Endast transkribering (snabbare)
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda --no-diarization

# Flera format
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda -f txt -f srt -f json
```

## 📋 Systemkrav

### Linux/WSL (Development)
- Python 3.12
- NVIDIA GPU med CUDA Compute Capability 6.0+
- NVIDIA Driver 525.60.13 eller nyare
- 8GB RAM (16GB rekommenderat)
- 10GB disk space

### Windows (Standalone)
Se [BUILD_WINDOWS.md](BUILD_WINDOWS.md) för instruktioner

## 🛠️ Installation

### Automatisk (Rekommenderat)

```bash
# GPU-läge (med CUDA-stöd)
bash scripts/start.sh gpu

# CPU-läge
bash scripts/start.sh cpu
```

### Manuell

```bash
# 1. Skapa virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Installera dependencies
pip install -r whisper_diarize/requirements.txt

# 3. Installera PyTorch med CUDA (Linux)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Konfigurera HuggingFace Token

För diarisering behöver du en HuggingFace-token:

1. Skapa konto på https://huggingface.co
2. Acceptera användarvillkor för: https://huggingface.co/pyannote/speaker-diarization-3.1
3. Skapa token: https://huggingface.co/settings/tokens
4. Kopiera `.env.example` till `.env` och lägg till din token:
   ```bash
   cp whisper_diarize/.env.example .env
   # Redigera .env och lägg till: HF_TOKEN=din_token_här
   ```

## 📖 Användning

### Webb-gränssnitt (Enklast)

```bash
source activate_cuda.sh
python -m whisper_diarize.webapp
```

Funktioner:
- ✅ Drag-and-drop filuppladdning
- ✅ Realtids progress tracking
- ✅ Välj språk, format, device (CUDA/CPU)
- ✅ Ladda ner resultat direkt

### Kommandoraden (CLI)

```bash
# Grundläggande användning
python -m whisper_diarize.main -i input.mp3 -o output_dir

# Avancerade alternativ
python -m whisper_diarize.main \
  -i input.mp3 \
  -o output_dir \
  --device cuda \
  --language sv \
  -f txt -f srt -f json \
  --whisper-model KBLab/kb-whisper-large

# Visa hjälp
python -m whisper_diarize.main --help
```

### Alternativ

- `-i, --input`: Input ljudfil (mp3, wav, etc.) [Required]
- `-o, --output`: Output-katalog (default: output)
- `-l, --language`: Språkkod (default: sv)
- `-f, --format`: Output-format (txt, srt, json, tsv) - kan användas flera gånger
- `--device`: Device (auto, cpu, cuda)
- `--whisper-model`: Whisper-modell att använda
- `--no-diarization`: Hoppa över diarisering (snabbare)
- `--merge-speakers`: Slå ihop segment från samma talare (default: on)

## 🎯 Performance

Med CUDA GPU-acceleration (RTX 5090):
- **2:48 min ljud**: ~10-15 sekunder transkribering + 15-20 sekunder diarisering
- **Total tid**: ~30 sekunder för komplett pipeline
- **CPU-läge**: 5-10x långsammare

## 📁 Output-format

### TXT
```
[SPEAKER_00] Detta är text från talare 1.
[SPEAKER_01] Detta är text från talare 2.
```

### SRT (Undertextformat)
```
1
00:00:00,000 --> 00:00:05,230
[SPEAKER_00] Detta är text från talare 1.

2
00:00:05,500 --> 00:00:10,120
[SPEAKER_01] Detta är text från talare 2.
```

### JSON
```json
[
  {
    "start": 0.0,
    "end": 5.23,
    "text": "Detta är text från talare 1.",
    "speaker": "SPEAKER_00"
  }
]
```

### TSV
```tsv
start	end	speaker	text
0.000	5.230	SPEAKER_00	Detta är text från talare 1.
0.500	10.120	SPEAKER_01	Detta är text från talare 2.
```

## 🪟 Windows Standalone-applikation

För att skapa en fristående Windows-executable:

1. **Snabbguide**: Se [BUILD_WINDOWS.md](BUILD_WINDOWS.md)
2. **Detaljerad guide**: Se [WINDOWS_STANDALONE.md](WINDOWS_STANDALONE.md)

Redo-att-använda filer:
- `launcher.py` - Windows launcher med auto-browser
- `whisper_diarize_windows.spec` - PyInstaller konfiguration

## 📚 Dokumentation

- [CLAUDE.md](CLAUDE.md) - Arkitektur och utvecklarguide
- [README_CUDA.md](README_CUDA.md) - CUDA-konfiguration och felsökning
- [BUILD_WINDOWS.md](BUILD_WINDOWS.md) - Snabbguide för Windows build
- [WINDOWS_STANDALONE.md](WINDOWS_STANDALONE.md) - Detaljerad Windows deployment-guide

## 🔧 Kända begränsningar

- **Torchcodec**: Använder soundfile som workaround (har ingen påverkan på funktionalitet)
- **FFmpeg**: Vissa varningar kan visas men påverkar inte funktionen
- **Första körning**: Laddar ner modeller (~1.5GB) - tar tid första gången
- **Windows SmartScreen**: Unsigned exe kan trigga varning (se Windows-guide för code signing)

## 🐛 Felsökning

### CUDA fungerar inte

```bash
# Verifiera CUDA-installation
nvidia-smi

# Verifiera PyTorch CUDA-stöd
source activate_cuda.sh
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Diarisering misslyckas

Vanliga orsaker:
1. HF_TOKEN inte konfigurerad → Se installation
2. Användarvillkor ej accepterade → Gå till https://huggingface.co/pyannote/speaker-diarization-3.1
3. Token ogiltig → Skapa ny token på https://huggingface.co/settings/tokens

### Långsam på CPU

Detta är normalt. För snabbare bearbetning:
1. Använd GPU med CUDA
2. Eller använd `--no-diarization` för snabbare transkribering

## 📄 Licens

Se LICENSE för detaljer.

## 🙏 Erkännanden

Detta projekt använder:
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Optimerad Whisper-implementation
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization
- [KBLab kb-whisper](https://huggingface.co/KBLab) - Svenska Whisper-modeller
- [Flask](https://flask.palletsprojects.com/) - Webb-gränssnitt

## 🤝 Bidra

Bidrag välkomnas! Skapa gärna issues eller pull requests.

## 📧 Support

För frågor och support, skapa en issue på GitHub.

---

**Gjord med ❤️ för svensk tal-till-text**
