#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-cpu}"
echo "==> Startar Whisper Diarize ($MODE)"

# 1) venv
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2) pip
python -m pip install --upgrade pip wheel setuptools

# 3) krav
pip install -r whisper_diarize/requirements.txt

# 4) GPU (Linux/WSL)
if [[ "$MODE" == "gpu" ]]; then
  echo "Installerar PyTorch CUDA 12.1"
  pip install --index-url https://download.pytorch.org/whl/cu121 torch torchaudio --upgrade
fi

# 5) HF cache symlink fix (Windows inte relevant här, men ofarligt)
export HF_HUB_DISABLE_SYMLINKS=1

# 6) Verifiera CUDA
python - <<'PY'
import torch
print('torch', torch.__version__)
print('cuda_available', torch.cuda.is_available())
if torch.cuda.is_available():
  print('cuda_device_count', torch.cuda.device_count())
PY

# 7) Starta Flask
python - <<'PY'
from whisper_diarize.webapp import run
run()
PY

