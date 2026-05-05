import os
from datetime import datetime
from audio_recorder import record_audio_manual
from gemini_processor import process_meeting_audio
from pdf_generator import save_to_pdf

def main():
    # 1. Tentukan folder output (Bisa Anda ganti sesuai keinginan)
    output_folder = "Hasil_Notulensi"
    
    # Buat foldernya otomatis jika belum ada
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_file = "temp_meeting.wav"

    # 2. Mulai merekam (Akan tertahan di sini sampai user tekan Ctrl + C)
    is_recorded = record_audio_manual(audio_file)

    # 3. Jika rekaman berhasil dihentikan dengan benar dan file ada
    if is_recorded and os.path.exists(audio_file):
        print("\n⏳ Sedang memproses dengan Gemini AI...")
        print("Mohon tunggu dan JANGAN TUTUP jendela ini, AI sedang merangkum meeting Anda...")
        
        # Proses ke Gemini
        hasil_ai = process_meeting_audio(audio_file)
        
        # 4. Simpan ke PDF di folder yang ditentukan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nama_file_pdf = f"Meeting_{timestamp}.pdf"
        path_pdf_lengkap = os.path.join(output_folder, nama_file_pdf)
        
        save_to_pdf(hasil_ai, filename=path_pdf_lengkap)
        
        # 5. Bersihkan file audio temp agar hardisk tidak penuh
        # os.remove(audio_file)
        
        # Mendapatkan path absolut untuk ditampilkan ke user
        absolute_path = os.path.abspath(path_pdf_lengkap)
        print("\n✅ PROSES SELESAI!")
        print(f"File PDF Anda berhasil disimpan di:\n-> {absolute_path}")
    else:
        print("\n❌ Proses dibatalkan atau gagal merekam audio.")

if __name__ == "__main__":
    main()