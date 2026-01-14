# CUDA-konfiguration för Whisper Diarize

Detta projekt är nu konfigurerat för att använda CUDA-acceleration på både transkribering och diarisering.

## Snabbstart

```bash
# Aktivera miljön med CUDA-stöd
source activate_cuda.sh

# Kör transkribering och diarisering med CUDA
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda
```

## Installation

Installation är redan klar med PyTorch 2.9.0+cu128. Om du behöver installera på nytt:

```bash
# Skapa virtual environment
python3 -m venv .venv

# Aktivera och installera dependencies
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r whisper_diarize/requirements.txt

# Installera PyTorch med CUDA 12.8-stöd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

## CUDA-verifiering

Systemet använder:
- **GPU**: NVIDIA GeForce RTX 5090 Laptop GPU
- **CUDA version**: 12.8
- **PyTorch**: 2.9.0+cu128
- **cuDNN**: 9.1.0

För att verifiera CUDA-installation:

```bash
source activate_cuda.sh
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

## Användning

### Med diarisering (identifiera talare)
```bash
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda -f txt -f srt -f json
```

### Utan diarisering (snabbare)
```bash
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cuda --no-diarization
```

### CPU-läge (om GPU inte är tillgängligt)
```bash
python -m whisper_diarize.main -i ljudfil.mp3 -o output --device cpu
```

## Prestandaförbättring

Med CUDA är transkriberingen cirka **10-15x snabbare** jämfört med CPU:
- **2:48 minuters audio**: ~10-15 sekunder på GPU vs ~3-5 minuter på CPU
- **Diarisering**: Körs också på GPU för snabbare bearbetning

## Tekniska detaljer

### Fixade problem
1. **cuDNN-bibliotek**: LD_LIBRARY_PATH konfigureras automatiskt av `activate_cuda.sh`
2. **pyannote.audio API**: Uppdaterad till version 4.x med stöd för `DiarizeOutput` objekt
3. **torchcodec**: Använder soundfile som workaround för ljudinläsning
4. **HuggingFace authentication**: `use_auth_token` ersatt med `token` parameter

### Använda compute types
- **CUDA (GPU)**: float16 (snabbt och effektivt)
- **CPU**: int8 (mindre minneskrävande)

## Felsökning

Om CUDA inte fungerar:

1. Verifiera att nvidia-smi visar ditt GPU
2. Kontrollera att LD_LIBRARY_PATH är satt (genom activate_cuda.sh)
3. Testa PyTorch CUDA-support:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

Om du får fel om cuDNN, se till att du använder `activate_cuda.sh` istället för vanlig venv-aktivering.
