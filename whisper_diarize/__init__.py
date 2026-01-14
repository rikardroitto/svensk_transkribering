"""
Whisper Diarize - Lokalt transkribering och talardiarisering för svenska ljudfiler
"""

# Apply torch load patch immediately before any other imports!
from . import torch_fix

__version__ = "1.0.0"
__author__ = "Whisper Diarize"
__description__ = "Lokalt transkribering och talardiarisering med Whisper och Pyannote"

from .transcribe import transcribe_audio
from .diarize import diarize_audio
from .merge import merge_transcription_and_speakers, merge_consecutive_same_speaker
from .export import export_results

__all__ = [
    "transcribe_audio",
    "diarize_audio",
    "merge_transcription_and_speakers",
    "merge_consecutive_same_speaker",
    "export_results",
]
