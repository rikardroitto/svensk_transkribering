"""
Whisper transkribering med faster-whisper
"""

import os
from typing import List, Dict
from faster_whisper import WhisperModel
from tqdm import tqdm
from .config import WHISPER_MODEL


def transcribe_audio(
    audio_path: str,
    language: str,
    device: str,
    compute_type: str
) -> List[Dict]:
    """
    Transkribera ljudfil med Whisper.

    Args:
        audio_path: Sökväg till ljudfilen
        language: Språkkod (t.ex. "sv" för svenska)
        device: "cuda" eller "cpu"
        compute_type: "float16", "float32", eller "int8"

    Returns:
        List[Dict]: Lista med segments: [{"start": float, "end": float, "text": str}, ...]

    Raises:
        FileNotFoundError: Om ljudfilen inte finns
        Exception: Om modelladdning eller transkribering misslyckas
    """
    # Validera att filen existerar
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Ljudfilen hittades inte: {audio_path}")

    print(f"📝 Laddar Whisper-modell: {WHISPER_MODEL}")

    try:
        # Ladda modellen
        model = WhisperModel(
            WHISPER_MODEL,
            device=device,
            compute_type=compute_type
        )
    except Exception as e:
        raise Exception(f"Kunde inte ladda Whisper-modellen: {e}")

    print(f"🎙️  Transkriberar: {os.path.basename(audio_path)}")

    try:
        # Transkribera
        segments_iterator, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection för bättre segmentering
            vad_parameters=dict(
                min_silence_duration_ms=500
            )
        )

        # Samla alla segment med progress bar
        segments = []
        duration = info.duration

        with tqdm(total=int(duration), unit="s", desc="Transkribering") as pbar:
            last_end = 0
            for segment in segments_iterator:
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })

                # Uppdatera progress bar
                progress = int(segment.end - last_end)
                pbar.update(progress)
                last_end = segment.end

        print(f"✅ Transkribering klar: {len(segments)} segment")
        return segments

    except Exception as e:
        raise Exception(f"Transkribering misslyckades: {e}")
