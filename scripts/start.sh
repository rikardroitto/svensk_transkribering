#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-cpu}"
echo "==> Whisper Diarize ($MODE)"

# 1) Skapa venv om det inte finns
if [[ ! -d .venv ]]; then
  echo "Skapar virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2) Uppgradera pip
python -m pip install --upgrade pip wheel setuptools -q

# 3) Installera PyTorch FÖRST (innan requirements som drar in torch som dependency)
if [[ "$MODE" == "gpu" ]]; then
  echo "Installerar PyTorch med CUDA 12.8 (RTX 5090)..."
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128 -q
else
  echo "Installerar PyTorch (CPU)..."
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu -q
fi

# 4) Installera övriga dependencies (använder redan installerad torch)
echo "Installerar dependencies..."
pip install -r whisper_diarize/requirements.txt -q
pip install soundfile -q

# 5) Miljövariabler
export HF_HUB_DISABLE_SYMLINKS=1

# 6) Sätt LD_LIBRARY_PATH för CUDA-bibliotek
if [[ "$MODE" == "gpu" ]]; then
  VENV_PATH=$(pwd)/.venv/lib/python3.12/site-packages
  export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:$VENV_PATH/nvidia/cudnn/lib:$VENV_PATH/nvidia/cublas/lib:$VENV_PATH/nvidia/cuda_runtime/lib"
fi

# 7) Verifiera installation
echo ""
python - <<'PY'
import torch
print(f"PyTorch {torch.__version__}")
if torch.cuda.is_available():
    print(f"CUDA: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA: Ej tillgänglig (CPU-läge)")
PY
echo ""

# 8) Starta webapp
echo "Startar webbserver på http://127.0.0.1:5000"
python run_webapp.py
