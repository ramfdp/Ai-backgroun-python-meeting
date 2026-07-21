import os
from datetime import datetime
from gemini_processor import process_meeting_audio
from pdf_generator import save_to_pdf
from word_generator import export_to_word

import tkinter as tk
from tkinter import filedialog

def upload_audio():
    print("Membuka jendela untuk memilih file...")
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Force dialog to front
    
    audio_file = filedialog.askopenfilename(
        title="Pilih file audio", 
        parent=root,
        filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.flac *.ogg"), ("All Files", "*.*")]
    )

    if not audio_file:
        print("❌ Batal memilih file.")
        return

    if os.path.exists(audio_file):
        print("\n⏳ Sedang memproses dengan Gemini AI...")
        hasil_ai = process_meeting_audio(audio_file)
        
        os.makedirs("Hasil_Notulensi", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_path = os.path.join("Hasil_Notulensi", f"Meeting_{timestamp}.pdf")
        word_path = os.path.join("Hasil_Notulensi", f"Meeting_{timestamp}.docx")
        
        save_to_pdf(hasil_ai, filename=pdf_path)
        export_to_word(hasil_ai, filename=word_path)
        
        print(f"\n✅ PROSES SELESAI!\nFile PDF Anda berhasil disimpan di:\n-> {os.path.abspath(pdf_path)}")
        print(f"File Word Anda berhasil disimpan di:\n-> {os.path.abspath(word_path)}")
    else:
        print("❌ File tidak ditemukan.")

if __name__ == "__main__":
    upload_audio()