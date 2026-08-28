import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import queue
import keyboard # ponytail: minimal dependency for global 'esc' detection
import warnings # ponytail: suppress annoying soundcard warnings
import os
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore", message="data discontinuity in recording")


STORAGE_FOLDERS = ("Rekaman", "Hasil Tuning", "Transkrip", "Analisis Lengkap")


def desktop_path():
    if os.name == "nt":
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "Desktop")
            return Path(os.path.expandvars(value))
        except OSError:
            pass
    return Path.home() / "Desktop"


def new_recording_path(desktop=None, now=None):
    root = Path(desktop or desktop_path()) / "Hermes Transkrip"
    for folder in STORAGE_FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return root / "Rekaman" / f"Meeting_{timestamp}.wav"


def audio_status(mixed_data):
    return "🔊 Suara terdeteksi...  " if np.max(np.abs(mixed_data)) > 0.05 else "⏳ Menunggu suara...    "


def process_saved_recording(filename, processor=None):
    if processor is None:
        from hermes_processor import process_recording
        processor = process_recording
    return processor(Path(filename))


def record_audio_manual(filename=None):
    filename = Path(filename) if filename else new_recording_path()
    filename.parent.mkdir(parents=True, exist_ok=True)
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
    print("Tekan ESC atau CTRL + C pada keyboard untuk BERHENTI merekam")
    print("==================================================")

    try:
        with sf.SoundFile(filename, mode='w', samplerate=sample_rate, channels=channels) as file:
            while True:
                if keyboard.is_pressed('esc'):
                    raise KeyboardInterrupt

                data_l = q_loopback.get()
                data_a = q_asli.get()     

                mixed_data = data_l + (data_a * 4.0)
                
                mixed_data = np.clip(mixed_data, -1.0, 1.0)
                file.write(mixed_data)

                # ponytail: one threshold, independently testable
                print(audio_status(mixed_data), end=chr(13), flush=True)

    except KeyboardInterrupt:
        print("\n[OK] Perekaman dihentikan manual oleh Anda.")
        is_recording = False 
        
        t1.join()
        t2.join()
        print(f"[OK] Rekaman tersimpan di: {filename.resolve()}")
        try:
            process_saved_recording(filename)
        except Exception as e:
            print(f"[ERROR] Rekaman aman, tetapi pemrosesan gagal: {e}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat mixing: {e}")
        is_recording = False
        return False


if __name__ == "__main__":
    record_audio_manual()