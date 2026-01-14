param(
  [string]$Mode = "cpu"  # "cpu" eller "gpu"
)

$ErrorActionPreference = "Stop"
Write-Host "==> Startar Whisper Diarize ($Mode)" -ForegroundColor Cyan

# 1) Venv
if (-not (Test-Path .venv)) {
  Write-Host "Skapar virtualenv .venv" -ForegroundColor Yellow
  python -m venv .venv
}

Write-Host "Aktiverar .venv" -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# 2) Uppgradera pip
python -m pip install --upgrade pip wheel setuptools

# 3) Installera baskrav
pip install -r whisper_diarize/requirements.txt

# 4) Valfritt: Installera PyTorch med CUDA
if ($Mode -eq "gpu") {
  Write-Host "Försöker installera PyTorch (CUDA 12.1)" -ForegroundColor Yellow
  pip install --index-url https://download.pytorch.org/whl/cu121 torch torchaudio --upgrade
}

# 5) Miljöfix för Windows symlänkar (HF cache)
$env:HF_HUB_DISABLE_SYMLINKS = "1"

# 6) Verifiera CUDA
python - << 'PY'
import torch
print('torch', torch.__version__)
print('cuda_available', torch.cuda.is_available())
if torch.cuda.is_available():
  print('cuda_device_count', torch.cuda.device_count())
  for i in range(torch.cuda.device_count()):
    try:
      print(f'[{i}]', torch.cuda.get_device_name(i))
    except Exception:
      pass
PY

# 7) Starta Flask
python - << 'PY'
from whisper_diarize.webapp import run
run()
PY

