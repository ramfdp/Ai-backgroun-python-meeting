"""Plugin Hermes untuk transkripsi dan notulensi meeting."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MENU = """## Transkrip Meeting

Silakan pilih layanan:

1. **Mulai Rekam Meeting (Live AI)**
2. **Upload File Audio (.wav/.mp3/.m4a) Manual**
3. **Kompresi Suara Noise dan Generate Notulensi**
4. **Analisis Lengkap Percakapan dari PDF**
5. **Keluar transkrip**

Jalankan `/transkrip 1` sampai `/transkrip 5` sesuai pilihan.
"""


def _audio_python() -> list[str]:
    candidates = [[sys.executable]]
    if os.name == "nt":
        candidates += [["py", f"-{version}"] for version in ("3.11", "3.12", "3.10", "3.14")]
    for candidate in candidates:
        probe = subprocess.run(
            candidate + ["-c", "import soundcard, soundfile, numpy, keyboard"],
            capture_output=True,
            timeout=10,
        )
        if probe.returncode == 0:
            return candidate
    raise RuntimeError("Dependency audio belum tersedia. Instal requirements.txt plugin terlebih dahulu.")


def _launch_recorder() -> None:
    if os.name != "nt":
        raise RuntimeError("Perekaman Mic + Speaker tahap ini hanya mendukung Windows.")
    script = ROOT / "audio_recorder.py"
    if not script.exists():
        raise RuntimeError("audio_recorder.py tidak ditemukan di folder plugin.")
    command = subprocess.list2cmdline(_audio_python() + [str(script)])
    subprocess.Popen(
        ["cmd.exe", "/k", f"title Transkrip Meeting && {command}"],
        cwd=ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def handle_transkrip(raw_args: str = "", launch_recorder=None) -> str:
    choice = (raw_args or "").strip()
    if not choice:
        return MENU
    if choice != "1":
        return "Pilihan tersebut belum diaktifkan pada tahap ini. Gunakan `/transkrip 1`."
    try:
        (launch_recorder or _launch_recorder)()
    except Exception as error:
        return f"Gagal membuka recorder: {error}"
    return "CMD rekaman dibuka. Tekan ESC atau CTRL+C di jendela tersebut untuk berhenti."


def register(ctx) -> None:
    ctx.register_command(
        "transkrip",
        handle_transkrip,
        description="Buka menu transkripsi dan notulensi meeting.",
        args_hint="[1-5]",
    )
