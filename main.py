import os
from datetime import datetime
from audio_recorder import record_audio_manual
from gemini_processor import process_meeting_audio
from pdf_generator import save_to_pdf
from word_generator import export_to_word

def main():
    output_folder = "Hasil_Notulensi"
    os.makedirs(output_folder, exist_ok=True)

    audio_file = "temp_meeting.wav"

    try:
        is_recorded = record_audio_manual(audio_file)
    except KeyboardInterrupt:
        print("\nProses dibatalkan.")
        try:
            os.remove(audio_file)
            print("\nFile audio dihapus karna dibatalkan.")
        except:
            pass
        return

    if not is_recorded or not os.path.exists(audio_file):
        print("\nProses dibatalkan atau gagal merekam audio.")
        return

    print("\n⏳ Sedang memproses dengan Gemini AI...")
    print("Mohon tunggu dan JANGAN TUTUP jendela ini, AI sedang merangkum meeting Anda...")

    hasil_ai = process_meeting_audio(audio_file)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_file_txt = f"Meeting_{timestamp}.txt"
    path_txt_lengkap = os.path.join(output_folder, nama_file_txt)
    
    try:
        with open(path_txt_lengkap, "w", encoding="utf-8") as f:
            f.write(hasil_ai)
    except Exception as e:
        print(f"⚠️ Gagal menyimpan backup TXT: {e}")
        
    nama_file_pdf = f"Meeting_{timestamp}.pdf"
    path_pdf_lengkap = os.path.join(output_folder, nama_file_pdf)
    
    try:
        save_to_pdf(hasil_ai, filename=path_pdf_lengkap)
        absolute_path = os.path.abspath(path_pdf_lengkap)
        
        path_word_lengkap = os.path.join(output_folder, f"Meeting_{timestamp}.docx")
        export_to_word(hasil_ai, filename=path_word_lengkap)
        absolute_path_word = os.path.abspath(path_word_lengkap)
        
        print("\n✅ PROSES SELESAI!")
        print(f"File PDF Anda berhasil disimpan di:\n-> {absolute_path}")
        print(f"File Word Anda berhasil disimpan di:\n-> {absolute_path_word}")
        print(f"(Backup teks juga tersedia di: {os.path.abspath(path_txt_lengkap)})")
    except Exception as e:
        absolute_path_txt = os.path.abspath(path_txt_lengkap)
        print(f"\n❌ Gagal membuat PDF: {e}")
        print(f"✅ JANGAN KHAWATIR, data Anda aman. Backup teks (TXT) berhasil disimpan di:\n-> {absolute_path_txt}")

if __name__ == "__main__":
    main()