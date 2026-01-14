WHISPER DIARIZE - KOM IGÅNG
===========================

FÖRUTSÄTTNINGAR
---------------
- Python 3.12
- Hugging Face-konto med token (https://huggingface.co/settings/tokens)
- Acceptera villkoren för pyannote-modellen:
  https://huggingface.co/pyannote/speaker-diarization-3.1

INSTALLATION
------------
1. Skapa och aktivera virtuell miljö:

   # Linux/Mac:
   bash scripts/start.sh cpu    # För CPU
   bash scripts/start.sh gpu    # För GPU med CUDA

   # Windows PowerShell:
   .\scripts\start.ps1 cpu
   .\scripts\start.ps1 gpu

2. Skapa .env fil med din Hugging Face-token:

   cp whisper_diarize/.env.example .env

   Redigera .env och sätt:
   HF_TOKEN=din_token_här

STARTA PROGRAMMET
-----------------
Webbgränssnitt (rekommenderat):

   python -m whisper_diarize.webapp

   Öppna sedan http://localhost:5000 i webbläsaren.

Kommandorad:

   python -m whisper_diarize.main -i ljudfil.mp3 -o output

   Fler alternativ:
   -f txt srt json tsv    Välj format
   --no-diarization       Hoppa över talaridentifiering
   --device cpu           Tvinga CPU-läge

FELSÖKNING
----------
"Token saknas" / "401 Unauthorized":
  - Kontrollera att .env innehåller rätt HF_TOKEN
  - Acceptera villkoren på huggingface.co/pyannote/speaker-diarization-3.1

Långsam körning:
  - Använd GPU om möjligt
  - Använd --no-diarization för snabbare körning utan talaridentifiering

Första körningen tar extra tid - modeller laddas ner (~3GB).
