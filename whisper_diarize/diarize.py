"""
Talardiarisering med pyannote.audio
"""

import os
from typing import List, Dict
import torch
import soundfile as sf
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

    print(f"Laddar diariseringsmodell: {DIARIZATION_MODEL}")

    try:
        # Säkerställ att token finns
        if not hf_token:
            raise Exception(
                "Hugging Face-token saknas. Sätt HF_TOKEN i .env eller miljövariabeln "
                "och acceptera användarvillkoren för pyannote/speaker-diarization-3.1."
            )

        # Ladda pipeline
        pipeline = Pipeline.from_pretrained(
            DIARIZATION_MODEL,
            token=hf_token
        )

        # Vissa felvägar kan returnera None istället för att kasta exception
        if pipeline is None or not callable(getattr(pipeline, "__call__", None)):
            raise Exception(
                "Kunde inte ladda diariseringspipen. Kontrollera att din token är giltig "
                "och att du accepterat villkoren på https://huggingface.co/pyannote/speaker-diarization-3.1."
            )

        # Flytta till GPU om tillgänglig
        if torch.cuda.is_available():
            try:
                pipeline = pipeline.to(torch.device("cuda"))
            except Exception as move_err:
                print(f"Varning: Kunde inte flytta diariseringsmodell till CUDA: {move_err}")
                print("Fortsätter på CPU...")

    except Exception as e:
        msg = str(e)
        if any(code in msg for code in ["401", "403"]) or "gated" in msg or "private" in msg:
            raise Exception(
                f"Kunde inte autentisera med Hugging Face. "
                f"Kontrollera att:\n"
                f"  1. Din token är giltig\n"
                f"  2. Du har accepterat användarvillkoren för {DIARIZATION_MODEL}\n"
                f"Fel: {e}"
            )
        raise Exception(f"Kunde inte ladda diariseringsmodellen: {e}")

    print(f"Diariserar: {os.path.basename(audio_path)}")

    try:
        # Ladda ljudfil med soundfile (workaround för torchcodec-problem)
        waveform, sample_rate = sf.read(audio_path)

        # Konvertera till torch tensor och lägg till channel-dimension om behövs
        waveform_tensor = torch.from_numpy(waveform).float()
        if waveform_tensor.ndim == 1:
            # Mono: lägg till channel-dimension (1, samples)
            waveform_tensor = waveform_tensor.unsqueeze(0)
        else:
            # Stereo: transponera till (channels, samples)
            waveform_tensor = waveform_tensor.T

        # Skapa audio dictionary för pyannote
        audio_dict = {
            "waveform": waveform_tensor,
            "sample_rate": sample_rate
        }

        # Kör diarisering med preloaded audio
        diarization = pipeline(audio_dict)

        # Konvertera till lista av dictionaries
        segments = []
        # Nyare pyannote.audio 4.x använder DiarizeOutput objekt
        if hasattr(diarization, 'itertracks'):
            # Äldre API (pyannote.audio 3.x)
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
        elif hasattr(diarization, 'speaker_diarization'):
            # Nyare API (pyannote.audio 4.x) - använd speaker_diarization attribute
            annotation = diarization.speaker_diarization
            for segment, _, speaker in annotation.itertracks(yield_label=True):
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": speaker
                })
        else:
            raise Exception("Kunde inte hitta diariseringsdata i outputen")

        # Räkna unika talare
        unique_speakers = len(set(seg["speaker"] for seg in segments))
        print(f"Diarisering klar: {len(segments)} segment, {unique_speakers} talare")

        return segments

    except TypeError as e:
        # Fångar NoneType is not callable och liknande
        raise Exception(
            "Diarisering misslyckades: Pipen verkar inte ha laddats korrekt. "
            "Verifiera HF-token och åtkomst till modellen, och försök igen."
        )
    except Exception as e:
        raise Exception(f"Diarisering misslyckades: {e}")
