import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import queue

def record_audio_manual(filename="temp_meeting.wav"):
    sample_rate = 16000 
    channels = 1        
    chunk_size = 4000   # Merekam per 0.25 detik agar sinkron dan ringan
    
    try:
        # 1. Siapkan jalur Loopback (Suara dari GMeet/layar untuk teman meeting)
        default_speaker = sc.default_speaker()
        mic_loopback = sc.get_microphone(id=str(default_speaker.name), include_loopback=True)
        
        # 2. Siapkan jalur Asli (Microphone fisik untuk suara Anda)
        mic_asli = sc.default_microphone()
    except Exception as e:
        print(f"[ERROR] Gagal mendeteksi perangkat audio: {e}")
        return False

    # Antrean (Queue) untuk menampung sinyal suara dari kedua jalur
    q_loopback = queue.Queue()
    q_asli = queue.Queue()
    
    is_recording = True

    # --- THREAD 1: Menangkap suara teman meeting ---
    def record_loopback():
        with mic_loopback.recorder(samplerate=sample_rate, channels=channels) as rec:
            while is_recording:
                data = rec.record(numframes=chunk_size)
                q_loopback.put(data)

    # --- THREAD 2: Menangkap suara Anda ---
    def record_asli():
        with mic_asli.recorder(samplerate=sample_rate, channels=channels) as rec:
            while is_recording:
                data = rec.record(numframes=chunk_size)
                q_asli.put(data)

    # Mulai menjalankan kedua thread secara paralel
    t1 = threading.Thread(target=record_loopback)
    t2 = threading.Thread(target=record_asli)
    t1.start()
    t2.start()

    print("==================================================")
    print("🔴 REKAMAN MEETING DIMULAI (Mode: Mic + Speaker)")
    print("Tekan CTRL + C pada keyboard untuk BERHENTI merekam")
    print("==================================================")

    try:
        # Buka file untuk ditulis secara streaming
        with sf.SoundFile(filename, mode='w', samplerate=sample_rate, channels=channels) as file:
            while True:
                # 1. Ambil potongan gelombang suara dari kedua antrean
                data_l = q_loopback.get() # Suara teman (Gmeet)
                data_a = q_asli.get()     # Suara mentah Anda (Microphone)

                # --- FITUR AUDIO AMPLIFIER (PENGUAT VOLUME) ---
                # Kalikan data suara Anda agar volumenya naik. 
                # Angka 4.0 berarti volume mic Anda dibesarkan 400%.
                # Anda bisa mengubah angka ini (misal 3.0 atau 5.0) sesuai kebutuhan.
                pengali_volume_mic = 4.0 
                data_a_diperbesar = data_a * pengali_volume_mic

                # 2. MIXING AUDIO: Menjumlahkan gelombang suara
                mixed_data = data_l + data_a_diperbesar
                
                # 3. NORMALISASI (Clipping)
                # Mencegah suara pecah (distorsi) jika Anda tertawa keras
                # karena volume sudah dikali 4.
                mixed_data = np.clip(mixed_data, -1.0, 1.0)

                # Tulis hasil campuran ke hardisk
                file.write(mixed_data)

    except KeyboardInterrupt:
        print("\n[OK] Perekaman dihentikan manual oleh Anda.")
        is_recording = False # Kirim sinyal mati ke dalam thread
        
        # Tunggu kedua thread menyelesaikan sisa antreannya (Graceful Shutdown)
        t1.join()
        t2.join()
        return True
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat mixing: {e}")
        is_recording = False
        return False