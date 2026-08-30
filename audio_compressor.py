import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from audio_recorder import STORAGE_FOLDERS, desktop_path
from hermes_processor import process_recording


SUPPORTED_AUDIO = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def tingkatkan_vokal_dan_simpan(file_input, file_output):
    print("1. Membaca file audio...")
    seg = AudioSegment.from_file(file_input).set_frame_rate(16000).set_channels(1).set_sample_width(2)
    y = np.array(seg.get_array_of_samples(), dtype=np.float32) / 32768.0
    sr = seg.frame_rate

    print("2. Membersihkan background noise...")
    audio_bersih = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.90)

    print("3. Memproses audio...")
    audio_int = (audio_bersih * 32767).astype(np.int16)
    sound = AudioSegment(
        audio_int.tobytes(),
        frame_rate=sr,
        sample_width=audio_int.dtype.itemsize,
        channels=1,
    )

    print("4. Tuning: Melakukan dorongan pada Vokal (EQ & Normalization)...")
    sound = sound.high_pass_filter(200)
    sound = sound.low_pass_filter(10000)
    sound = normalize(sound)

    print("5. Menyimpan ke format MP3...")
    sound.export(file_output, format="mp3", bitrate="192k")
    print(f"🎉 Selesai! Audio dengan vokal tebal dan jelas tersimpan di: {file_output}")


def compress_and_process(selected=None, processor=None, desktop=None, now=None, tuner=None):
    print("Membuka jendela untuk memilih file...")
    if selected is None:
        window = tk.Tk()
        window.withdraw()
        try:
            selected = filedialog.askopenfilename(
                title="Pilih file audio",
                filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.flac *.ogg")],
            )
        finally:
            window.destroy()

    if not selected:
        print("❌ Batal memilih file.")
        return None

    source = Path(selected)
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in SUPPORTED_AUDIO:
        raise ValueError("Format audio harus .wav/.mp3/.m4a/.flac/.ogg")

    root = Path(desktop or desktop_path()) / "Hermes Transkrip"
    for folder in STORAGE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    tuned = root / "Hasil Tuning" / f"Tuning_{stamp}_{source.stem}.mp3"
    (tuner or tingkatkan_vokal_dan_simpan)(source, tuned)
    return (processor or process_recording)(tuned)


def main():
    return compress_and_process()

if __name__ == "__main__":
    main()
