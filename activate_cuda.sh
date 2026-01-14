#!/usr/bin/env bash
# Activation script för Whisper Diarize med CUDA-stöd
#
# Användning:
#   source activate_cuda.sh
#
# Detta script aktiverar virtual environment och sätter nödvändiga miljövariabler
# för att CUDA ska fungera korrekt med PyTorch och pyannote.audio

# Aktivera virtual environment
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment aktiverat"
else
    echo "✗ Fel: .venv/bin/activate hittades inte"
    echo "  Kör: python3 -m venv .venv && pip install -r whisper_diarize/requirements.txt"
    return 1
fi

# Sätt LD_LIBRARY_PATH för CUDA-bibliotek
VENV_PATH=$(pwd)/.venv/lib/python3.12/site-packages
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$VENV_PATH/nvidia/cudnn/lib:$VENV_PATH/nvidia/cublas/lib:$VENV_PATH/nvidia/cuda_runtime/lib

echo "✓ CUDA library paths konfigurerade"

# Verifiera CUDA-tillgänglighet
echo ""
echo "Verifierar CUDA..."
python -c "import torch; print(f'  PyTorch: {torch.__version__}'); print(f'  CUDA tillgänglig: {torch.cuda.is_available()}'); print(f'  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Miljö redo för transkribering med CUDA!"
    echo ""
    echo "Exempel:"
    echo "  python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda"
    echo "  python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda --no-diarization"
else
    echo ""
    echo "✗ Kunde inte verifiera CUDA-installation"
fi
