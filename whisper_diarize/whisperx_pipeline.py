"""
WhisperX pipeline för förbättrad diarisering och transkribering.
"""

import os
import torch
import whisperx
from whisperx.diarize import DiarizationPipeline
import gc
from typing import List, Dict, Optional
from .config import DIARIZATION_MODEL, HF_TOKEN, DEFAULT_LANGUAGE


def check_gpu_status():
    """Debug GPU availability and capabilities"""
    print("=" * 60)
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        cuda_version = torch.version.cuda
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✓ GPU detekterad och funktionell")
        print(f"   Namn: {device_name}")
        print(f"   CUDA Version: {cuda_version}")
        print(f"   GPU Minne: {gpu_memory:.1f} GB")
        print(f"   Använder GPU-acceleration")
        return "cuda"
    else:
        print("✗ Ingen GPU tillgänglig - kör på CPU (LÅNGSAMT)")
        print(f"   torch.cuda.is_available() = False")
        print(f"   CUDA_VISIBLE_DEVICES = {os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')}")
        return "cpu"
    print("=" * 60)


def process_audio_whisperx(
    audio_path: str,
    num_speakers: Optional[int] = None,
    device: str = "cuda",
    batch_size: int = 16,
    compute_type: str = "float16",
    language: str = DEFAULT_LANGUAGE
) -> List[Dict]:
    """
    Kör hela pipeline med WhisperX: Transkribe -> Align -> Diarize.
    """
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Ljudfilen hittades inte: {audio_path}")

    print(f"Startar WhisperX-processering för: {audio_path}")
    
    # Check GPU status first
    actual_device = check_gpu_status()
    
    # Override if user requested CPU
    if device == "cpu":
        actual_device = "cpu"
        compute_type = "int8"
    elif actual_device == "cpu":
        compute_type = "int8"
    
    # 1. Transkribering
    model_name = "large-v2" 
    print(f"Laddar Whisper-modell: {model_name} på {actual_device}")
    
    try:
        model = whisperx.load_model(
            model_name, 
            actual_device, 
            compute_type=compute_type, 
            language=language
        )
        print(f"✓ Whisper-modell laddad på {actual_device}")
    except Exception as e:
        print(f"✗ Kunde inte ladda Whisper på {actual_device}: {e}")
        if actual_device == "cuda":
            print("   Faller tillbaka till CPU...")
            actual_device = "cpu"
            compute_type = "int8"
            model = whisperx.load_model(
                model_name, 
                actual_device, 
                compute_type=compute_type, 
                language=language
            )
        else:
            raise

    # Transkribera
    print("Transkriberar...")
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size)
    print(f"✓ Transkribering klar: {len(result.get('segments', []))} segment")
    
    # Frigör minne
    del model
    gc.collect()
    if actual_device == "cuda":
        torch.cuda.empty_cache()
    
    # 2. Alignment
    print(f"Kör alignment på {actual_device}...")
    try:
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], 
            device=actual_device
        )
        
        result = whisperx.align(
            result["segments"], 
            model_a, 
            metadata, 
            audio, 
            actual_device, 
            return_char_alignments=False
        )
        print("✓ Alignment klar")
    except Exception as e:
        print(f"✗ Alignment misslyckades: {e}")
        raise
    
    # Frigör minne
    del model_a
    gc.collect()
    if actual_device == "cuda":
        torch.cuda.empty_cache()
    
    # 3. Diarisering - ALLTID försök GPU först, separat från ovanstående
    # Pyannote kan ha annan GPU-kompatibilitet än Whisper
    diarize_device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Diariserar med modell: {DIARIZATION_MODEL} på {diarize_device}")
    
    try:
        diarize_model = DiarizationPipeline(
            use_auth_token=HF_TOKEN, 
            device=diarize_device
        )
        print(f"✓ Diariseringsmodell laddad på {diarize_device}")
    except Exception as e:
        print(f"✗ Kunde inte ladda diariseringsmodell på {diarize_device}: {e}")
        if diarize_device == "cuda":
            print("   Faller tillbaka till CPU för diarisering...")
            diarize_device = "cpu"
            diarize_model = DiarizationPipeline(
                use_auth_token=HF_TOKEN, 
                device=diarize_device
            )
        else:
            raise
    
    print("Kör diarisering (detta kan ta några minuter)...")
    try:
        diarize_segments = diarize_model(
            audio, 
            min_speakers=num_speakers, 
            max_speakers=num_speakers
        )
        print("✓ Diarisering klar")
    except Exception as e:
        print(f"✗ Diarisering misslyckades: {e}")
        raise
    
    # 4. Tilldela talare
    print("Tilldelar talare till segment...")
    result = whisperx.assign_word_speakers(diarize_segments, result)
    
    # Formatera output
    final_segments = []
    for seg in result["segments"]:
        final_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
            "speaker": seg.get("speaker", "UNKNOWN")
        })
        
    print(f"✓ Klar! {len(final_segments)} segment skapade.")
    return final_segments
