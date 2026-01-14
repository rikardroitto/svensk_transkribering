# Repository Guidelines

## Project Structure & Modules
- `whisper_diarize/`: Core package and CLI entry (`main.py`, `transcribe.py`, `diarize.py`, `merge.py`, `export.py`, `utils.py`, `config.py`).
- `output/`: Generated artifacts (TXT, SRT, JSON, TSV). Safe to delete.
- `.env.example` / `.env`: Set `HF_TOKEN` for pyannote; do not commit secrets.
- Sample media like `ljudfil.mp3` may live at repo root during development.

## Build, Run, and Dev Commands
- Install deps (Torch/torchaudio must be preinstalled):
  - `pip install -r whisper_diarize/requirements.txt`
- Run CLI (basic):
  - `python -m whisper_diarize.main -i ljudfil.mp3 -o output`
- Advanced examples:
  - `python -m whisper_diarize.main -i file.mp3 -f txt srt json tsv`
  - `python -m whisper_diarize.main -i file.mp3 --no-diarization`
  - `python -m whisper_diarize.main -i file.mp3 --device cpu`
- Configure token:
  - Copy `.env.example` to `.env` and set `HF_TOKEN=...` or export as env var.

## Coding Style & Naming
- Language: Python 3.12. Follow PEP 8, 4‑space indentation.
- Names: `snake_case` for modules/functions, `PascalCase` for classes, constants UPPER_SNAKE.
- Types & docs: Use type hints and short, factual docstrings.
- UX strings: Keep user‑facing CLI messages in Swedish to match README.

## Testing Guidelines
- Framework: `pytest` (not included yet). Place tests in `tests/`, name files `test_*.py`.
- Quick run: `pytest -q`.
- Fixtures: Keep audio fixtures small (<1MB) under `tests/fixtures/`; avoid committing large binaries.
- Aim for unit tests around `merge.py`, `export.py`, and utility functions; use dependency injection/mocking for model calls.

## Commit & Pull Request Guidelines
- Commits: Imperative, concise, scoped. Swedish is fine. Example: `Lägg till TSV‑export och tester`.
- PRs: Include summary, rationale, CLI examples (command + produced files), environment notes (CPU/GPU), and linked issues. Add before/after snippets where helpful.

## Security & Configuration Tips
- Do not commit `.env` or tokens. The repo already ignores `.env` and `output/`.
- Respect requirement note: do not pin/install Torch via `requirements.txt`; use existing local install.
