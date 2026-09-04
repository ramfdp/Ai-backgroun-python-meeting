"""Plugin Hermes untuk transkripsi dan notulensi meeting."""

from __future__ import annotations

import shutil
import subprocess
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED_IMPORTS = ("faster_whisper", "soundcard", "soundfile", "numpy", "fpdf", "keyboard", "pydub", "noisereduce", "docx")
_SETUP_ERROR = None
MENU = """## Transkrip Meeting

Silakan pilih layanan:

1. **Mulai Rekam Meeting (Live AI)**
2. **Upload File Audio (.wav/.mp3/.m4a) Manual**
3. **Kompresi Suara Noise dan Generate Notulensi**
4. **Analisis Lengkap Percakapan dari TXT**
5. **Keluar transkrip**

Jalankan `/transkrip 1` sampai `/transkrip 5` sesuai pilihan.
"""


def _dependencies_ready() -> bool:
    return all(importlib.util.find_spec(name) is not None for name in REQUIRED_IMPORTS)


def ensure_dependencies(run=None, uv=None) -> None:
    if _dependencies_ready():
        return
    requirements = ROOT / "requirements.txt"
    if not requirements.is_file():
        raise RuntimeError("requirements.txt tidak ditemukan di folder plugin")
    print("[transkrip-meeting] Menginstal dependencies, mohon tunggu...")
    runner = run or subprocess.run
    uv = uv or shutil.which("uv")
    if uv:
        command = [uv, "pip", "install", "--python", sys.executable, "-r", str(requirements)]
    else:
        runner([sys.executable, "-m", "ensurepip", "--upgrade"], check=True, cwd=ROOT)
        command = [sys.executable, "-m", "pip", "install", "-r", str(requirements)]
    runner(
        command,
        check=True,
        cwd=ROOT,
    )
    importlib.invalidate_caches()
    if not _dependencies_ready():
        raise RuntimeError("Instalasi selesai tetapi dependencies belum dapat dimuat")
    print("[transkrip-meeting] Instalasi selesai. /transkrip siap digunakan.")


def _launch_script(script_name: str) -> None:
    if sys.platform != "win32":
        raise RuntimeError("Fitur ini tahap ini hanya mendukung Windows.")
    script = ROOT / script_name
    if not script.exists():
        raise RuntimeError(f"{script_name} tidak ditemukan di folder plugin.")
    subprocess.Popen(
        [sys.executable, str(script)],
        cwd=ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def _launch_recorder() -> None:
    _launch_script("audio_recorder.py")


def _launch_uploader() -> None:
    _launch_script("upload_audio.py")


def _launch_compressor() -> None:
    _launch_script("audio_compressor.py")


def _launch_txt_analysis() -> None:
    _launch_script("conversation_analysis.py")


def handle_transkrip(
    raw_args: str = "",
    launch_recorder=None,
    launch_uploader=None,
    launch_compressor=None,
    launch_txt_analysis=None,
) -> str:
    if _SETUP_ERROR:
        return f"Plugin transkrip belum siap: {_SETUP_ERROR}"
    choice = (raw_args or "").strip()
    if not choice:
        return "✅ Plugin transkrip siap digunakan.\n\n" + MENU
    try:
        if choice == "1":
            (launch_recorder or _launch_recorder)()
            return "CMD rekaman dibuka. Tekan ESC atau CTRL+C di jendela tersebut untuk berhenti."
        if choice == "2":
            (launch_uploader or _launch_uploader)()
            return "Window upload audio dibuka. Pilih file .wav/.mp3/.m4a."
        if choice == "3":
            (launch_compressor or _launch_compressor)()
            return "Window kompresi audio dibuka. Pilih file audio."
        if choice == "4":
            (launch_txt_analysis or _launch_txt_analysis)()
            return "Window analisis TXT dibuka. Pilih file .txt."
        if choice == "5":
            return "Operasi transkrip dibatalkan."
        return "Pilihan tidak valid. Gunakan `/transkrip 1` sampai `/transkrip 5`."
    except Exception as error:
        return f"Gagal membuka pilihan {choice}: {error}"


def register(ctx) -> None:
    global _SETUP_ERROR
    try:
        ensure_dependencies()
        _SETUP_ERROR = None
    except Exception as error:
        _SETUP_ERROR = str(error)
        print(f"[transkrip-meeting] Instalasi dependencies gagal: {_SETUP_ERROR}")
    ctx.register_command(
        "transkrip",
        handle_transkrip,
        description="Buka menu transkripsi dan notulensi meeting.",
        args_hint="[1-5]",
    )
