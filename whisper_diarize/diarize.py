"""
Talardiarisering med pyannote.audio
"""

import os
from typing import List, Dict
import torch
from pyannote.audio import Pipeline
from .config import DIARIZATION_MODEL


def diarize_audio(audio_path: str, hf_token: str) -> List[Dict]:
    """
    Diarisera ljudfil för att identifiera olika talare.

    Args:
        audio_path: Sökväg till ljudfilen
        hf_token: Hugging Face token för att ladda modellen

    Returns:
        List[Dict]: Lista med talarsegment: [{"start": float, "end": float, "speaker": str}, ...]

    Raises:
        FileNotFoundError: Om ljudfilen inte finns
        Exception: Om modelladdning eller diarisering misslyckas
    """
    # Validera att filen existerar
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Ljudfilen hittades inte: {audio_path}")

    print(f"👥 Laddar diariseringsmodell: {DIARIZATION_MODEL}")

    try:
        # Ladda pipeline
        pipeline = Pipeline.from_pretrained(
            DIARIZATION_MODEL,
            use_auth_token=hf_token
        )

        # Flytta till GPU om tillgänglig
        if torch.cuda.is_available():
            pipeline = pipeline.to(torch.device("cuda"))

    except Exception as e:
        if "401" in str(e) or "403" in str(e):
            raise Exception(
                f"Kunde inte autentisera med Hugging Face. "
                f"Kontrollera att:\n"
                f"  1. Din token är giltig\n"
                f"  2. Du har accepterat användarvillkoren för {DIARIZATION_MODEL}\n"
                f"Fel: {e}"
            )
        raise Exception(f"Kunde inte ladda diariseringsmodellen: {e}")

    print(f"🔍 Diariserar: {os.path.basename(audio_path)}")

    try:
        # Kör diarisering
        diarization = pipeline(audio_path)

        # Konvertera till lista av dictionaries
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        # Räkna unika talare
        unique_speakers = len(set(seg["speaker"] for seg in segments))
        print(f"✅ Diarisering klar: {len(segments)} segment, {unique_speakers} talare")

        return segments

    except Exception as e:
        raise Exception(f"Diarisering misslyckades: {e}")
