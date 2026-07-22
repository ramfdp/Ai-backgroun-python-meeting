import sys
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize
from pydub import utils as pydub_utils
import numpy as np
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from gemini_processor import process_meeting_audio
from pdf_generator import save_to_pdf
from word_generator import export_to_word


def _setup_ffmpeg():
    # ponytail: point pydub at bundled ffmpeg when running as .exe
    if getattr(sys, 'frozen', False):
        ffmpeg_dir = os.path.join(sys._MEIPASS, 'ffmpeg_bin')
    else:
        ffmpeg_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg_bin')
    ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    if os.path.isfile(ffmpeg_path):
        pydub_utils.FFMPEG_PATH = ffmpeg_path
        AudioSegment.converter = ffmpeg_path

_setup_ffmpeg()


def tingkatkan_vokal_dan_simpan(file_input, file_output):
    print("1. Membaca file audio...")
    # ponytail: pydub replaces librosa.load — no external audioread/ffmpeg path needed
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


def main():
    print("Membuka jendela untuk memilih file...")
    root = tk.Tk()
    root.withdraw()
    file_rekaman_hp = filedialog.askopenfilename(
        title="Pilih file audio",
        filetypes=[
            ("Audio Files", "*.wav *.mp3 *.m4a *.flac *.ogg"),
            ("All Files", "*.*"),
        ],
    )

    if not file_rekaman_hp:
        print("❌ Batal memilih file.")
        return 

    hasil_vokal_jelas = "output-sound-dituning.mp3"
    tingkatkan_vokal_dan_simpan(file_rekaman_hp, hasil_vokal_jelas)

    print("\n⏳ Sedang memproses dengan Gemini AI...")
    hasil_ai = process_meeting_audio(hasil_vokal_jelas)

    os.makedirs("Hasil_Notulensi", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = os.path.join("Hasil_Notulensi", f"Meeting_{timestamp}.pdf")
    word_path = os.path.join("Hasil_Notulensi", f"Meeting_{timestamp}.docx")
    
    save_to_pdf(hasil_ai, filename=pdf_path)
    export_to_word(hasil_ai, filename=word_path)

    print(
        f"\n✅ PROSES SELESAI!\nFile PDF Anda berhasil disimpan di:\n-> {os.path.abspath(pdf_path)}\n"
        f"File Word Anda berhasil disimpan di:\n-> {os.path.abspath(word_path)}"
    )

if __name__ == "__main__":
    main()
