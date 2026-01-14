# Whisper Diarize

Ett robust, lokalt Python-program för transkribering och talardiarisering av svenska ljudfiler. Programmet är forskningsetiskt säkert - ingen data lämnar din dator.

## Översikt

Whisper Diarize kombinerar:
- **Faster-Whisper**: Optimerad Whisper-implementation för transkribering
- **Pyannote.audio**: Avancerad talardiarisering (speaker diarization)

### Funktioner

✅ Lokalt - ingen data skickas till cloud/API
✅ Stöd för både CPU och GPU med automatisk fallback
✅ Progress reporting under körning
✅ Hantera RTX 5090 (sm_120) gracefully
✅ Flera exportformat (TXT, SRT, JSON, TSV)
✅ Svensk optimerad med KBLab Whisper-modell

## Installation

### 1. Förutsättningar

- Python 3.12
- PyTorch och torchaudio redan installerat
- Hugging Face-konto med accepterade Pyannote användarvillkor

### 2. Installera dependencies

```bash
pip install -r requirements.txt
```

**Viktigt**: Installera INTE nya versioner av torch/torchaudio - programmet använder din befintliga installation.

### 3. Konfigurera Hugging Face token

Kopiera `.env.example` till `.env` och sätt din Hugging Face token:

```bash
cp whisper_diarize/.env.example .env
# Redigera .env och lägg till din token
```

I `.env` filen:
```bash
HF_TOKEN=din_huggingface_token_här
```

För att få en token:
1. Gå till https://huggingface.co/settings/tokens
2. Skapa en ny token (read access räcker)
3. Acceptera användarvillkoren för `pyannote/speaker-diarization-3.1`

**Alternativ**: Du kan också sätta miljövariabeln direkt:
```bash
export HF_TOKEN=din_token_här
python -m whisper_diarize.main -i audio.mp3
```

## Användning

### Grundläggande användning

```bash
python -m whisper_diarize.main -i audio.mp3 -o output
```

Detta kommer:
1. Transkribera ljudfilen
2. Identifiera olika talare
3. Exportera resultat till `output/audio.txt` och `output/audio.srt`

### Avancerade alternativ

```bash
# Exportera till flera format
python -m whisper_diarize.main -i audio.mp3 -o results -f txt srt json tsv

# Hoppa över diarisering (snabbare, ingen talaridentifiering)
python -m whisper_diarize.main -i audio.mp3 --no-diarization

# Tvinga CPU-läge
python -m whisper_diarize.main -i audio.mp3 --device cpu

# Specificera språk (default är svenska)
python -m whisper_diarize.main -i audio.mp3 -l en
```

### CLI-alternativ

| Alternativ | Kort | Beskrivning | Default |
|------------|------|-------------|---------|
| `--input` | `-i` | Input ljudfil (obligatorisk) | - |
| `--output` | `-o` | Output-katalog | `output` |
| `--language` | `-l` | Språkkod | `sv` |
| `--format` | `-f` | Output-format (kan användas flera gånger) | `txt srt` |
| `--device` | - | Device: auto, cpu, eller cuda | `auto` |
| `--no-diarization` | - | Hoppa över talardiarisering | `False` |
| `--merge-speakers` | - | Slå ihop segment från samma talare | `True` |

## Output-format

### TXT
Enkel text med talaridentifikation:
```
[SPEAKER_00] Hej och välkommen till programmet.
[SPEAKER_01] Tack, kul att vara här!
```

### SRT
Standard undertextformat:
```
1
00:00:00,000 --> 00:00:05,000
[SPEAKER_00] Hej och välkommen till programmet.

2
00:00:05,100 --> 00:00:08,500
[SPEAKER_01] Tack, kul att vara här!
```

### JSON
Fullständig data i JSON-format:
```json
[
  {
    "start": 0.0,
    "end": 5.0,
    "text": "Hej och välkommen till programmet.",
    "speaker": "SPEAKER_00"
  },
  {
    "start": 5.1,
    "end": 8.5,
    "text": "Tack, kul att vara här!",
    "speaker": "SPEAKER_01"
  }
]
```

### TSV
Tab-separerade värden (lätt att importera i Excel/Pandas):
```
start   end     speaker     text
0.000   5.000   SPEAKER_00  Hej och välkommen till programmet.
5.100   8.500   SPEAKER_01  Tack, kul att vara här!
```

## Exempel på körning

```
🎙️  Whisper Diarize v1.0
==================================================

[1/6] Validerar input...
✅ Input: interview.mp3

[2/6] Skapar output-katalog...
✅ Output: output

[3/6] Detekterar device...
✅ CUDA tillgänglig, använder GPU
🖥️  Device: cuda (float32)

[4/6] Transkriberar ljud...
📝 Laddar Whisper-modell: KBLab/kb-whisper-medium
🎙️  Transkriberar: interview.mp3
Transkribering: 100%|████████| 154/154 [02:34<00:00]
✅ Transkribering klar: 145 segment

[5/6] Diariserar talare...
👥 Laddar diariseringsmodell: pyannote/speaker-diarization-3.1
🔍 Diariserar: interview.mp3
✅ Diarisering klar: 89 segment, 3 talare
🔗 Kombinerar transkribering och talare...
🔀 Slår ihop segment från samma talare...

[6/6] Exporterar resultat...
  ✓ output/interview.txt
  ✓ output/interview.srt

==================================================
✅ Klart!
📊 Sammanfattning:
   • Segment: 62
   • Talare: 3
   • Längd: 02:34
   • Format: txt, srt
```

## Troubleshooting

### CUDA-problem

**Problem**: `CUDA out of memory`
**Lösning**: Använd CPU-läge med `--device cpu`

**Problem**: `sm_120 architecture warnings`
**Lösning**: Programmet faller automatiskt tillbaka på CPU vid instabilitet

### Token-problem

**Problem**: `401 Unauthorized` eller `403 Forbidden`
**Lösning**:
1. Kontrollera att din token är korrekt satt i `.env` filen eller som miljövariabel
2. Acceptera användarvillkoren på https://huggingface.co/pyannote/speaker-diarization-3.1

**Problem**: Token saknas (tom sträng)
**Lösning**:
1. Skapa `.env` fil från `.env.example`: `cp whisper_diarize/.env.example .env`
2. Lägg till din token i `.env` filen
3. Eller sätt miljövariabeln: `export HF_TOKEN=din_token_här`

### Långsam körning

**Tips för snabbare körning**:
- Använd GPU om tillgängligt
- Använd `--no-diarization` för att hoppa över talardiarisering
- Kortare ljudfiler processar snabbare

### Installationsproblem

**Problem**: `No module named 'faster_whisper'`
**Lösning**: Kör `pip install -r requirements.txt`

**Problem**: Torch-versionskonflikt
**Lösning**: Använd din befintliga torch-installation, installera INTE nya versioner

## Tekniska detaljer

### Modeller

- **Whisper**: `KBLab/kb-whisper-medium` - Svensk optimerad modell
- **Diarisering**: `pyannote/speaker-diarization-3.1` - State-of-the-art diarization

### Systemkrav

- **Minne**: 4GB RAM (CPU), 6GB VRAM (GPU)
- **Lagring**: ~3GB för modeller
- **Processor**: Multi-core rekommenderat

### Performance

Ungefärliga tider för 10 minuters ljud:
- **CPU (Intel i7)**: ~15-20 minuter
- **GPU (RTX 3090)**: ~3-5 minuter
- **GPU (RTX 5090)**: ~2-3 minuter (om stöd finns)

## Projektstruktur

```
whisper_diarize/
├── __init__.py           # Paket definition
├── config.py             # Konfiguration (tokens, modeller)
├── transcribe.py         # Whisper transkribering
├── diarize.py            # Pyannote diarisering
├── merge.py              # Kombinera transkript + talare
├── export.py             # Exportera till olika format
├── utils.py              # Helper functions
├── main.py               # CLI entrypoint
├── requirements.txt      # Dependencies
└── README.md             # Denna fil
```

## Forskningsetik

Detta program är designat för forskningsetisk användning:
- ✅ All processing sker lokalt
- ✅ Ingen data skickas till externa servrar
- ✅ Full kontroll över dina ljudfiler
- ✅ Inga loggar eller telemetri

## Licens

Fri att använda för forskning och privat bruk. Se respektive modellers licenser:
- Whisper: MIT License
- Pyannote: MIT License

## Support

För problem eller frågor, kontrollera först:
1. Troubleshooting-sektionen ovan
2. Att alla dependencies är installerade
3. Att din Hugging Face token fungerar

## Utveckling

Vill du bidra eller modifiera? Koden är välstrukturerad och kommenterad:
- Varje modul har tydligt ansvar
- Funktioner har docstrings
- Error handling är konsekvent
- Progress reporting för användarvänlighet
