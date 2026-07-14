import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import queue

def record_audio_manual(filename="temp_meeting.wav"):
    sample_rate = 16000 
    channels = 1        
    chunk_size = 4000   
    
    try:
        default_speaker = sc.default_speaker()
        mic_loopback = sc.get_microphone(id=str(default_speaker.name), include_loopback=True) #loopback = suara orang lain
        mic_asli = sc.default_microphone() #suara anda
    except Exception as e:
        print(f"[ERROR] Gagal mendeteksi perangkat audio: {e}")
        return False

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

    t1 = threading.Thread(target=record_loopback)
    t2 = threading.Thread(target=record_asli)
    t1.start()
    t2.start()

    print("==================================================")
    print("🔴 REKAMAN MEETING DIMULAI (Mode: Mic + Speaker)")
    print("Tekan CTRL + C pada keyboard untuk BERHENTI merekam")
    print("==================================================")

    try:
        with sf.SoundFile(filename, mode='w', samplerate=sample_rate, channels=channels) as file:
            while True:
                data_l = q_loopback.get()
                data_a = q_asli.get()     

                mixed_data = data_l + (data_a * 4.0)
                
                mixed_data = np.clip(mixed_data, -1.0, 1.0)
                file.write(mixed_data)

    except KeyboardInterrupt:
        print("\n[OK] Perekaman dihentikan manual oleh Anda.")
        is_recording = False 
        
        t1.join()
        t2.join()
        return True
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat mixing: {e}")
        is_recording = False
        return False