"""
Konfigurationsfil för Whisper Diarize
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ladda .env fil om den finns
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Hugging Face token - läs från miljövariabel
# Sätt HF_TOKEN miljövariabel eller skapa en .env fil från .env.example
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Modeller
WHISPER_MODEL = "KBLab/kb-whisper-medium"
DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"

# Standardinställningar
DEFAULT_LANGUAGE = "sv"
DEFAULT_OUTPUT_FORMATS = ["txt", "srt"]
