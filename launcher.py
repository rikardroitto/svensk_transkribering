"""
Windows Launcher för Whisper Diarize
Startar Flask-servern och öppnar webbläsaren automatiskt

Användning:
    För development: python launcher.py
    För PyInstaller: se WINDOWS_STANDALONE.md
"""
import os
import sys
import webbrowser
import time
import threading
from pathlib import Path


def setup_environment():
    """Konfigurera miljövariabler för både development och production"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        print(f"Kör som PyInstaller bundle från: {base_path}")

        # Sätt CUDA library paths för Windows
        cuda_paths = [
            base_path / "nvidia" / "cudnn" / "bin",
            base_path / "nvidia" / "cublas" / "bin",
            base_path / "nvidia" / "cuda_runtime" / "bin",
        ]

        path_str = os.environ.get("PATH", "")
        for cuda_path in cuda_paths:
            if cuda_path.exists():
                path_str = str(cuda_path) + os.pathsep + path_str
                print(f"  Lade till CUDA path: {cuda_path}")

        os.environ["PATH"] = path_str

        # Sätt output directory till användarmapp
        user_dir = Path.home() / "WhisperDiarize"
        user_dir.mkdir(exist_ok=True)
        os.environ["WD_OUTPUT_DIR"] = str(user_dir)
        print(f"Output directory: {user_dir}")
    else:
        # Development mode
        print("Kör i development mode")

    # Disable symlinks för HuggingFace (viktigt för Windows)
    os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

    # Kontrollera om .env finns och läs HF_TOKEN
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        if os.environ.get("HF_TOKEN"):
            print("✓ HF_TOKEN laddad från .env")
        else:
            print("⚠️  HF_TOKEN inte satt i .env - diarisering kanske inte fungerar")
    else:
        print("⚠️  .env fil saknas - skapa från .env.example")


def check_cuda():
    """Kontrollera CUDA-tillgänglighet och ge användarvänliga meddelanden"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✓ CUDA tillgänglig: {gpu_name}")
            print(f"✓ GPU-acceleration aktiverad - snabb bearbetning!")
            return True
        else:
            print("=" * 60)
            print("⚠️  GPU-ACCELERATION INTE TILLGÄNGLIG")
            print()
            print("Programmet kommer att fungera, men långsammare (CPU-läge)")
            print()
            print("Möjliga orsaker:")
            print("  1. Du har inget NVIDIA grafikkort")
            print("  2. NVIDIA driver är inte installerad")
            print("  3. NVIDIA driver är för gammal (behöver 525.60.13+)")
            print()
            print("Vad du kan göra:")
            print("  • Kontrollera grafikkort: Windows > Enhetshanteraren")
            print("  • Uppdatera driver: https://www.nvidia.com/drivers")
            print()
            print("⏱️  Beräknad tid för 3 min ljud:")
            print("     Med GPU: ~30 sekunder")
            print("     Med CPU: ~3-5 minuter")
            print("=" * 60)

            if getattr(sys, 'frozen', False):
                # I exe-läge, ge användaren tid att läsa
                print()
                input("Tryck Enter för att fortsätta med CPU-läge...")
            return False
    except ImportError:
        print("✗ PyTorch inte installerat")
        return False


def open_browser(url="http://127.0.0.1:5000", delay=3):
    """Öppna webbläsaren efter en kort fördröjning"""
    time.sleep(delay)
    print(f"\nÖppnar webbläsare: {url}")
    webbrowser.open(url)


def main():
    """Main entry point"""
    print("=" * 60)
    print("Whisper Diarize - Lokal transkribering och diarisering")
    print("=" * 60)
    print()

    # Setup environment
    setup_environment()
    print()

    # Check CUDA
    has_cuda = check_cuda()
    print()

    # Import Flask app (after environment setup)
    try:
        from whisper_diarize.webapp import run
    except ImportError as e:
        print(f"✗ Kunde inte importera webapp: {e}")
        print("\nKontrollera att alla dependencies är installerade:")
        print("  pip install -r whisper_diarize/requirements.txt")
        input("\nTryck Enter för att avsluta...")
        sys.exit(1)

    # Print startup info
    print("Startar server på http://127.0.0.1:5000")
    print("Webbläsaren öppnas automatiskt om några sekunder...")
    print()
    print("Tips:")
    print("  - Första körningen laddar ner modeller (~1.5GB)")
    if has_cuda:
        print("  - GPU-acceleration är aktiverad")
    else:
        print("  - CPU-läge (långsammare än GPU)")
    print("  - Tryck Ctrl+C för att stoppa servern")
    print()
    print("=" * 60)
    print()

    # Öppna browser i bakgrund
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Starta Flask
    try:
        run(host="127.0.0.1", port=5000)
    except KeyboardInterrupt:
        print("\n\nServern stoppades av användaren")
    except Exception as e:
        print(f"\n✗ Fel: {e}")
        import traceback
        traceback.print_exc()
        if getattr(sys, 'frozen', False):
            input("\nTryck Enter för att avsluta...")
        sys.exit(1)


if __name__ == "__main__":
    main()
