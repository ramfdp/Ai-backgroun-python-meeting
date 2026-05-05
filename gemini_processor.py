import os
import time
from google import genai

# Pastikan API Key Anda sudah diperbarui ya!
GEMINI_API_KEY = "AIzaSyBjTZbEyV4Sta8AQ5Pve4LPlYX_EHaAjnE"
client = genai.Client(api_key=GEMINI_API_KEY)

def process_meeting_audio(audio_path):
    print("\nMengunggah audio ke server Google...")
    try:
        # 1. Upload file audio
        audio_file = client.files.upload(file=audio_path)
        print(f"File berhasil diunggah. Menunggu server bersiap (15 detik)...")
        time.sleep(15) 
        
        prompt = """
        Anda adalah asisten notulensi profesional. Tugas Anda adalah mentranskripsikan file audio ini.
        
        ATURAN KETAT:
        1. Bahasa utama yang digunakan dalam meeting ini adalah Bahasa Indonesia.
        2. JANGAN MENGARANG ATAU BERHALUSINASI. Jika audio ini terdengar kosong atau sangat bising, Anda WAJIB membalas dengan: "SISTEM: Audio tidak terdeteksi atau terlalu bising."
        3. Jika ada suara percakapan, tuliskan transkripnya dan buatkan KESIMPULAN serta ACTION ITEMS di bawahnya.
        """
        
        print("Menganalisis audio... (Proses ini mungkin memakan waktu)")
        
        # --- LOGIKA RETRY UNTUK MENGATASI ERROR 503 ---
        maksimal_percobaan = 3
        
        for percobaan in range(maksimal_percobaan):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=[prompt, audio_file]
                )
                
                # Jika berhasil, hapus file dari server dan kembalikan teksnya
                client.files.delete(name=audio_file.name)
                return response.text
                
            except Exception as inner_e:
                pesan_error = str(inner_e)
                # Jika errornya adalah 503 (Server Penuh/Sibuk)
                if "503" in pesan_error or "UNAVAILABLE" in pesan_error:
                    waktu_tunggu = 20 * (percobaan + 1) # Tunggu makin lama: 20s, lalu 40s
                    print(f"⚠️ Server Google sedang penuh (Percobaan {percobaan + 1}/{maksimal_percobaan}).")
                    print(f"Menunggu {waktu_tunggu} detik sebelum mencoba lagi...")
                    time.sleep(waktu_tunggu)
                else:
                    # Jika errornya hal lain, langsung hentikan
                    client.files.delete(name=audio_file.name)
                    return f"SISTEM GAGAL: Terjadi kesalahan API: {pesan_error}"
        
        # Jika sudah mencoba 3 kali dan masih gagal
        client.files.delete(name=audio_file.name)
        return "SISTEM GAGAL: Tidak dapat memproses notulensi karena Server Google sedang mengalami gangguan tinggi (Error 503). Silakan coba jalankan meeting lagi nanti."
        
    except Exception as e:
        return f"SISTEM GAGAL: Terjadi kesalahan sistem: {e}"