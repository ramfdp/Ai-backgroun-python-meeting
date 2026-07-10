import os
from datetime import datetime
from gemini_processor import process_meeting_audio
from pdf_generator import save_to_pdf

# ponytail: raw input, no boilerplate CLI args
audio_file = input("Masukkan path file audio (contoh: C:\\path\\ke\\audio.wav): ").strip('\"\' ')

if os.path.exists(audio_file):
    print("\n⏳ Sedang memproses dengan Gemini AI...")
    hasil_ai = process_meeting_audio(audio_file)
    
    os.makedirs("Hasil_Notulensi", exist_ok=True)
    pdf_path = os.path.join("Hasil_Notulensi", f"Meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    save_to_pdf(hasil_ai, filename=pdf_path)
    
    print(f"\n✅ PROSES SELESAI!\nFile PDF Anda berhasil disimpan di:\n-> {os.path.abspath(pdf_path)}")
else:
    print("❌ File tidak ditemukan.")
