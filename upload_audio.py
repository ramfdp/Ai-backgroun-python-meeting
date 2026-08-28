from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from audio_recorder import STORAGE_FOLDERS, desktop_path
from hermes_processor import process_recording

SUPPORTED_AUDIO = {".wav", ".mp3", ".m4a"}


def choose_audio_file():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    try:
        return filedialog.askopenfilename(
            title="Pilih file audio meeting",
            filetypes=[("Audio meeting", "*.wav *.mp3 *.m4a")],
        )
    finally:
        root.destroy()


def import_and_process(selected=None, processor=None, desktop=None, now=None):
    selected = selected or choose_audio_file()
    if not selected:
        print("Upload audio dibatalkan.")
        return None

    source = Path(selected)
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in SUPPORTED_AUDIO:
        raise ValueError("Format audio harus .wav/.mp3/.m4a")

    root = Path(desktop or desktop_path()) / "Hermes Transkrip"
    for folder in STORAGE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)

    stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    destination = root / "Rekaman" / f"Upload_{stamp}_{source.name}"
    shutil.copy2(source, destination)
    print(f"Audio disalin ke: {destination}")
    return (processor or process_recording)(destination)


if __name__ == "__main__":
    try:
        import_and_process()
    except Exception as error:
        print(f"[ERROR] Upload atau pemrosesan gagal: {error}")
