import os
import time
from google import genai
from prompts import MEETING_PROMPT
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def process_meeting_audio(audio_path):
    print("\nMengunggah audio ke server Google...")
    try:
        audio_file = client.files.upload(file=audio_path)
        print(f"File berhasil diunggah. Menunggu server bersiap (15 detik)...")
        time.sleep(15) 
        
        print("Menganalisis audio... (Proses ini mungkin memakan waktu)")
        maksimal_percobaan = 3
        
        try:
            for percobaan in range(maksimal_percobaan):
                try:
                    current_model = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash") if percobaan == 0 else os.getenv("FALLBACK_MODEL", "gemini-3-flash-preview")
                    if percobaan > 0:
                        print(f"🔄 Beralih ke model fallback: {current_model}")
                        
                    response = client.models.generate_content(
                        model=current_model, 
                        contents=[MEETING_PROMPT, audio_file],
                        config=genai.types.GenerateContentConfig(temperature=0.0)
                    )
                    return response.text
                    
                except Exception as inner_e:
                    pesan_error = str(inner_e)
                    if "503" in pesan_error or "UNAVAILABLE" in pesan_error:
                        waktu_tunggu = 10 * (percobaan + 1) 
                        print(f"⚠️ Server Google penuh/error (Percobaan {percobaan + 1}/{maksimal_percobaan}).")
                        print(f"Menunggu {waktu_tunggu} detik sebelum mencoba lagi...")
                        time.sleep(waktu_tunggu)
                    else:
                        return f"SISTEM GAGAL: Terjadi kesalahan API: {pesan_error}"

            return "SISTEM GAGAL: Tidak dapat memproses notulensi karena Server Google sedang mengalami gangguan tinggi (Error 503). Silakan coba jalankan meeting lagi nanti."
        finally:
            client.files.delete(name=audio_file.name)
        
    except Exception as e:
        return f"SISTEM GAGAL: Terjadi kesalahan sistem: {e}"