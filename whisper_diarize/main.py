"""
Whisper Diarize - Lokalt transkribering och talardiarisering
CLI entrypoint
"""

import os
import sys
import click
from pathlib import Path

from .config import HF_TOKEN, DEFAULT_LANGUAGE, DEFAULT_OUTPUT_FORMATS
from .utils import get_optimal_device, format_duration
from .transcribe import transcribe_audio
from .diarize import diarize_audio
from .merge import merge_transcription_and_speakers, merge_consecutive_same_speaker
from .export import export_results


@click.command()
@click.option('--input', '-i', 'input_file', required=True,
              help='Input audio file (mp3, wav, etc.)')
@click.option('--output', '-o', 'output_dir', default='output',
              help='Output directory')
@click.option('--language', '-l', default=DEFAULT_LANGUAGE,
              help='Language code (default: sv for Swedish)')
@click.option('--format', '-f', 'formats', multiple=True, default=DEFAULT_OUTPUT_FORMATS,
              help='Output formats: txt, srt, json, tsv (can be used multiple times)')
@click.option('--device', default='auto',
              help='Device: auto (default), cpu, or cuda')
@click.option('--no-diarization', is_flag=True,
              help='Skip speaker diarization (faster, no speaker identification)')
@click.option('--merge-speakers', is_flag=True, default=True,
              help='Merge consecutive segments from same speaker')
def main(input_file, output_dir, language, formats, device, no_diarization, merge_speakers):
    """
    Whisper Diarize - Transkribera och diarisera ljudfiler lokalt

    Exempel:
      python -m whisper_diarize.main -i audio.mp3 -o results
      python -m whisper_diarize.main -i audio.mp3 -f txt srt json
    """
    print("🎙️  Whisper Diarize v1.0")
    print("=" * 50)

    # [1/6] Validera input
    print("\n[1/6] Validerar input...")
    if not os.path.exists(input_file):
        print(f"❌ Fel: Ljudfilen hittades inte: {input_file}")
        sys.exit(1)

    input_path = Path(input_file)
    print(f"✅ Input: {input_path.name}")

    # [2/6] Skapa output directory
    print("\n[2/6] Skapar output-katalog...")
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output: {output_dir}")

    # [3/6] Detektera device
    print("\n[3/6] Detekterar device...")
    if device == 'auto':
        device, compute_type = get_optimal_device()
    else:
        device = device.lower()
        compute_type = "float32" if device == "cuda" else "int8"

    print(f"🖥️  Device: {device} ({compute_type})")

    try:
        # [4/6] Transkribering
        print("\n[4/6] Transkriberar ljud...")
        transcription = transcribe_audio(
            audio_path=str(input_path),
            language=language,
            device=device,
            compute_type=compute_type
        )

        # [5/6] Diarisering (valfritt)
        if no_diarization:
            print("\n[5/6] Hoppar över diarisering...")
            # Lägg till dummy speaker för alla segment
            results = [
                {**seg, "speaker": "SPEAKER_00"}
                for seg in transcription
            ]
        else:
            print("\n[5/6] Diariserar talare...")
            speakers = diarize_audio(
                audio_path=str(input_path),
                hf_token=HF_TOKEN
            )

            print("🔗 Kombinerar transkribering och talare...")
            results = merge_transcription_and_speakers(transcription, speakers)

            # Slå ihop konsekutiva segment från samma talare
            if merge_speakers:
                print("🔀 Slår ihop segment från samma talare...")
                results = merge_consecutive_same_speaker(results)

        # [6/6] Exportera resultat
        print("\n[6/6] Exporterar resultat...")
        base_name = input_path.stem
        created_files = export_results(
            segments=results,
            output_dir=output_dir,
            base_name=base_name,
            formats=list(formats)
        )

        for file_path in created_files:
            print(f"  ✓ {file_path}")

        # Sammanfattning
        print("\n" + "=" * 50)
        unique_speakers = len(set(seg["speaker"] for seg in results))
        total_duration = results[-1]["end"] if results else 0

        print("✅ Klart!")
        print(f"📊 Sammanfattning:")
        print(f"   • Segment: {len(results)}")
        print(f"   • Talare: {unique_speakers}")
        print(f"   • Längd: {format_duration(total_duration)}")
        print(f"   • Format: {', '.join(formats)}")

    except FileNotFoundError as e:
        print(f"\n❌ Fel: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fel: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
