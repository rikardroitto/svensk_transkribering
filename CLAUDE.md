# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Whisper Diarize is a local Swedish audio transcription and speaker diarization system. It combines faster-whisper (for transcription) with pyannote.audio (for speaker identification) to produce timestamped, speaker-labeled transcripts in multiple formats.

The system has two interfaces:
- CLI: `whisper_diarize.main` - command-line tool for batch processing
- Web UI: `whisper_diarize.webapp` - Flask-based web interface for interactive use

## Core Architecture

### Processing Pipeline

The system follows a 6-stage pipeline in `main.py`:

1. **Input validation** - Verify audio file exists
2. **Output setup** - Create output directory
3. **Device detection** (`utils.py:get_optimal_device`) - Auto-detect CUDA/CPU and set compute type (float16 for GPU, int8 for CPU)
4. **Transcription** (`transcribe.py:transcribe_audio`) - Uses faster-whisper with VAD filtering to generate timestamped text segments
5. **Diarization** (`diarize.py:diarize_audio`) - Uses pyannote.audio to identify speakers (optional, can skip with `--no-diarization`)
6. **Merge & Export** - Combines transcription with speaker labels (`merge.py`), optionally merges consecutive segments from same speaker, then exports to selected formats (`export.py`)

### Key Module Responsibilities

- **transcribe.py**: Loads Whisper model and generates `[{"start": float, "end": float, "text": str}, ...]`
- **diarize.py**: Loads pyannote pipeline (requires HF_TOKEN) and generates `[{"start": float, "end": float, "speaker": str}, ...]`
- **merge.py**:
  - `merge_transcription_and_speakers()` - Maps speakers to transcription segments by maximum overlap
  - `merge_consecutive_same_speaker()` - Combines adjacent segments from same speaker (< 2s gap)
- **export.py**: Exports to TXT, SRT, JSON, TSV formats with speaker labels
- **config.py**: Loads .env file and defines model names (KBLab/kb-whisper-medium, pyannote/speaker-diarization-3.1)
- **webapp.py**: Flask app that wraps the pipeline with file upload and browser UI

### Configuration & Dependencies

- **Environment**: Requires `HF_TOKEN` in `.env` or environment variable. Users must accept pyannote/speaker-diarization-3.1 terms on HuggingFace.
- **PyTorch**: CRITICAL - Do NOT install torch/torchaudio via requirements.txt. Users must pre-install PyTorch with appropriate CUDA support. The `scripts/start.sh` handles this for setup.
- **Default models**: kb-whisper-medium (Swedish-optimized), pyannote speaker-diarization-3.1

## Development Commands

### Setup
```bash
# Create venv and install dependencies (CPU mode)
bash scripts/start.sh cpu

# GPU mode with CUDA 12.1
bash scripts/start.sh gpu
```

### Running the CLI
```bash
# Basic usage
python -m whisper_diarize.main -i ljudfil.mp3 -o output

# Multiple output formats
python -m whisper_diarize.main -i audio.mp3 -f txt srt json tsv

# Skip diarization (faster, no speaker identification)
python -m whisper_diarize.main -i audio.mp3 --no-diarization

# Force CPU device
python -m whisper_diarize.main -i audio.mp3 --device cpu

# Custom Whisper model
python -m whisper_diarize.main -i audio.mp3 --whisper-model KBLab/kb-whisper-large
```

### Running the Web UI
```bash
python -m whisper_diarize.webapp
# Or via the start script which launches webapp automatically
```

### Testing
```bash
# Run tests (pytest not yet included in requirements)
pytest -q

# Run specific test
pytest tests/test_merge.py -v
```

## Important Implementation Notes

### Device & Compute Type
- Auto-detection in `utils.py:get_optimal_device()` tries CUDA with test tensor, falls back to CPU on failure
- GPU uses float16 (best for faster-whisper), CPU uses int8
- Both transcription and diarization respect device selection, though diarization has its own GPU migration logic

### Speaker Merging Algorithm
- `merge_transcription_and_speakers()` uses overlap calculation - assigns speaker with maximum overlap duration to each transcription segment
- `merge_consecutive_same_speaker()` has hardcoded 2-second gap threshold - segments closer than this are merged if same speaker
- This threshold is defined inline at `merge.py:82` and may need adjustment for different use cases

### Error Handling Patterns
- File validation happens early (stage 1) with `FileNotFoundError`
- HF token issues raise explicit instructions about token setup and model terms acceptance
- CUDA instability is caught with fallback messaging

### UI/UX Conventions
- All user-facing CLI messages are in Swedish (print statements, error messages)
- Docstrings and code comments are in Swedish
- Progress bars use tqdm with segment-based updates

## File Structure Notes

- `output/` - Generated transcripts (safe to delete, gitignored)
- `scripts/` - Setup scripts for CPU/GPU modes
- Sample audio files (e.g., `ljudfil.mp3`) may exist at repo root during development
- `.env` contains sensitive HF_TOKEN (gitignored, use `.env.example` as template)

## Known Constraints

- PyTorch must be pre-installed with correct CUDA version for the system
- Pyannote models require HuggingFace authentication and user agreement to terms
- Speaker merging uses fixed 2s threshold (not configurable via CLI yet)
- Web UI has 100MB upload limit by default (configurable via `MAX_UPLOAD_MB` env var)
