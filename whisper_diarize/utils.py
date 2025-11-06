"""
Hjälpfunktioner för device detection och progress reporting
"""

import torch
from typing import Tuple


def get_optimal_device() -> Tuple[str, str]:
    """
    Detektera bästa device och compute type för systemet.

    Returns:
        Tuple[str, str]: (device, compute_type)
            - device: "cuda" eller "cpu"
            - compute_type: "float16", "float32", eller "int8"
    """
    if not torch.cuda.is_available():
        print("ℹ️  CUDA inte tillgänglig, använder CPU")
        return "cpu", "int8"

    try:
        # Testa CUDA genom att skapa en tensor
        test_tensor = torch.zeros(1).cuda()
        del test_tensor
        torch.cuda.empty_cache()

        # Använd float32 för kompatibilitet med sm_120 (RTX 5090)
        print("✅ CUDA tillgänglig, använder GPU")
        return "cuda", "float32"

    except Exception as e:
        print(f"⚠️  CUDA tillgänglig men instabil: {e}")
        print("Faller tillbaka på CPU")
        return "cpu", "int8"


def format_timestamp(seconds: float) -> str:
    """
    Formatera sekunder till SRT-format timestamp (HH:MM:SS,mmm)

    Args:
        seconds: Tid i sekunder

    Returns:
        str: Formaterad timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_duration(seconds: float) -> str:
    """
    Formatera sekunder till läsbar tidsformat (MM:SS)

    Args:
        seconds: Tid i sekunder

    Returns:
        str: Formaterad tid
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
