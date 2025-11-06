"""
Exportera resultat till olika format
"""

import json
from typing import List, Dict
from .utils import format_timestamp


def export_txt(segments: List[Dict], output_path: str) -> None:
    """
    Exportera till enkel textfil med talaridentifikation.

    Format: [SPEAKER_00] Text här

    Args:
        segments: Lista med segment
        output_path: Sökväg till output-fil
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            speaker = seg["speaker"]
            text = seg["text"]
            f.write(f"[{speaker}] {text}\n")


def export_srt(segments: List[Dict], output_path: str) -> None:
    """
    Exportera till SRT-format (undertextformat) med talare i texten.

    Format:
    1
    00:00:00,000 --> 00:00:05,000
    [SPEAKER_00] Text här

    Args:
        segments: Lista med segment
        output_path: Sökväg till output-fil
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_time = format_timestamp(seg["start"])
            end_time = format_timestamp(seg["end"])
            speaker = seg["speaker"]
            text = seg["text"]

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"[{speaker}] {text}\n")
            f.write("\n")


def export_json(segments: List[Dict], output_path: str) -> None:
    """
    Exportera till JSON-format med fullständig data.

    Args:
        segments: Lista med segment
        output_path: Sökväg till output-fil
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)


def export_tsv(segments: List[Dict], output_path: str) -> None:
    """
    Exportera till TSV-format (tab-separerade värden).

    Format: start\tend\tspeaker\ttext

    Args:
        segments: Lista med segment
        output_path: Sökväg till output-fil
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write("start\tend\tspeaker\ttext\n")

        # Data
        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            speaker = seg["speaker"]
            text = seg["text"].replace("\t", " ").replace("\n", " ")

            f.write(f"{start:.3f}\t{end:.3f}\t{speaker}\t{text}\n")


# Map format namn till exportfunktioner
EXPORT_FUNCTIONS = {
    "txt": export_txt,
    "srt": export_srt,
    "json": export_json,
    "tsv": export_tsv
}


def export_results(segments: List[Dict], output_dir: str, base_name: str, formats: List[str]) -> List[str]:
    """
    Exportera resultat till flera format.

    Args:
        segments: Lista med segment
        output_dir: Output-katalog
        base_name: Basnamn för filer (utan filändelse)
        formats: Lista med format att exportera till

    Returns:
        List[str]: Lista med skapade filsökvägar

    Raises:
        ValueError: Om ogiltigt format anges
    """
    created_files = []

    for fmt in formats:
        if fmt not in EXPORT_FUNCTIONS:
            raise ValueError(f"Ogiltigt format: {fmt}. Giltiga format: {list(EXPORT_FUNCTIONS.keys())}")

        output_path = f"{output_dir}/{base_name}.{fmt}"
        EXPORT_FUNCTIONS[fmt](segments, output_path)
        created_files.append(output_path)

    return created_files
