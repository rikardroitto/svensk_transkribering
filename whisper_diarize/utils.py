"""
Hjälpfunktioner för device detection och progress reporting
"""

from typing import Tuple
import torch


def get_optimal_device(verbose: bool = True) -> Tuple[str, str]:
    """
    Detektera bästa device och compute type för systemet.

    Args:
        verbose: Om True, skriv ut detaljerad information

    Returns:
        Tuple[str, str]: (device, compute_type)
            - device: "cuda" eller "cpu"
            - compute_type: "float16", "float32", eller "int8"
    """
    if not torch.cuda.is_available():
        if verbose:
            print("=" * 60)
            print("⚠️  CUDA inte tillgänglig")
            print("    Använder CPU-läge (långsammare)")
            print()
            print("    För GPU-acceleration:")
            print("    1. Kontrollera att du har en NVIDIA GPU")
            print("    2. Installera/uppdatera NVIDIA drivers")
            print("    3. Se till att PyTorch är installerat med CUDA-stöd")
            print("=" * 60)
        return "cpu", "int8"

    try:
        # Testa CUDA genom att skapa en tensor
        test_tensor = torch.zeros(1).cuda()
        del test_tensor
        torch.cuda.empty_cache()

        if verbose:
            gpu_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB

            print("=" * 60)
            print(f"✓ GPU detekterad och funktionell")
            print(f"   Namn: {gpu_name}")
            print(f"   CUDA Version: {cuda_version}")
            print(f"   GPU Minne: {gpu_memory:.1f} GB")
            print(f"   Använder GPU-acceleration")
            print("=" * 60)

        return "cuda", "float16"

    except Exception as e:
        if verbose:
            print("=" * 60)
            print(f"⚠️  CUDA tillgänglig men ej funktionell")
            print(f"    Fel: {str(e)[:100]}")
            print(f"    Faller tillbaka på CPU-läge")
            print()
            print("    Möjliga orsaker:")
            print("    - Inkompatibel GPU driver")
            print("    - CUDA libraries saknas eller är skadade")
            print("    - GPU används av en annan process")
            print("=" * 60)
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
