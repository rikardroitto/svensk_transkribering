"""
Kombinera transkribering och talardiarisering
"""

from typing import List, Dict


def merge_transcription_and_speakers(
    transcription: List[Dict],
    speakers: List[Dict]
) -> List[Dict]:
    """
    Kombinera transkriberade segment med talaridentifiering.

    För varje transkriberingssegment, hitta överlappande talarsegment
    och välj den talare som överlappar mest.

    Args:
        transcription: Lista med transkriberade segment
            [{"start": float, "end": float, "text": str}, ...]
        speakers: Lista med talarsegment
            [{"start": float, "end": float, "speaker": str}, ...]

    Returns:
        List[Dict]: Kombinerad lista
            [{"start": float, "end": float, "text": str, "speaker": str}, ...]
    """
    merged = []

    for trans_seg in transcription:
        trans_start = trans_seg["start"]
        trans_end = trans_seg["end"]
        trans_text = trans_seg["text"]

        # Hitta överlappande talarsegment
        best_speaker = "UNKNOWN"
        max_overlap = 0

        for speaker_seg in speakers:
            speaker_start = speaker_seg["start"]
            speaker_end = speaker_seg["end"]

            # Beräkna överlapp
            overlap_start = max(trans_start, speaker_start)
            overlap_end = min(trans_end, speaker_end)
            overlap_duration = max(0, overlap_end - overlap_start)

            # Uppdatera om detta är det längsta överlappet
            if overlap_duration > max_overlap:
                max_overlap = overlap_duration
                best_speaker = speaker_seg["speaker"]

        # Lägg till kombinerat segment
        merged.append({
            "start": trans_start,
            "end": trans_end,
            "text": trans_text,
            "speaker": best_speaker
        })

    return merged


def merge_consecutive_same_speaker(segments: List[Dict]) -> List[Dict]:
    """
    Slå ihop konsekutiva segment från samma talare.

    Args:
        segments: Lista med segment

    Returns:
        List[Dict]: Sammanslagna segment
    """
    if not segments:
        return []

    merged = []
    current = segments[0].copy()

    for seg in segments[1:]:
        # Om samma talare och nära i tid (< 2 sekunder mellanrum)
        if (seg["speaker"] == current["speaker"] and
            seg["start"] - current["end"] < 2.0):
            # Slå ihop
            current["end"] = seg["end"]
            current["text"] += " " + seg["text"]
        else:
            # Ny talare eller för stort gap, spara och börja nytt
            merged.append(current)
            current = seg.copy()

    # Lägg till sista segmentet
    merged.append(current)

    return merged
