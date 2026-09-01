import os
import sys

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

# ponytail: set ffmpeg+ffprobe globally before any pydub import
def _setup_ffmpeg():
    if getattr(sys, 'frozen', False):
        ffdir = os.path.join(sys._MEIPASS, 'ffmpeg_bin')
    else:
        ffdir = os.path.join(os.path.dirname(__file__), 'ffmpeg_bin')

    ffmpeg_ok = os.path.isfile(os.path.join(ffdir, 'ffmpeg.exe'))
    ffprobe_ok = os.path.isfile(os.path.join(ffdir, 'ffprobe.exe'))

    if ffmpeg_ok and ffprobe_ok:
        os.environ['PATH'] = ffdir + os.pathsep + os.environ.get('PATH', '')
    else:
        print(f"⚠️ ffmpeg_bin tidak lengkap di: {ffdir}")
        print(f"   ffmpeg.exe: {'✓' if ffmpeg_ok else '✗ HILANG'}")
        print(f"   ffprobe.exe: {'✓' if ffprobe_ok else '✗ HILANG'}")

_setup_ffmpeg()

from main import main as jalankan_rekaman
from upload import upload_audio as jalankan_upload
from audio_compressor import main as jalankan_kompresi
from conversation_analysis import analyze_pdf_conversation


def bersihkan_layar():
    print("\033[2J\033[H", end="")


def tunggu():
    input("\nTekan ENTER untuk kembali ke menu...")


def main():
    while True:
        bersihkan_layar()

        print("         SISTEM AI NOTULENSI MEETING v2.0")
        print("=" * 65)
        print("1. Mulai Rekam Meeting (Live AI)")
        print("2. Upload File Audio (.wav/.mp3/.m4a) Manual")
        print("3. Kompresi Suara Noise dan Generate Notulensi")
        print("4. Analisis Lengkap Percakapan dari PDF")
        print("5. Keluar Aplikasi")
        print("=" * 65)

        pilihan = input("\nMasukkan angka pilihan Anda (1/2/3/4/5): ").strip()

        try:
            if pilihan == "1":
                jalankan_rekaman()
                tunggu()

            elif pilihan == "2":
                jalankan_upload()
                tunggu()

            elif pilihan == "3":
                jalankan_kompresi()
                tunggu()

            elif pilihan == "4":
                analyze_pdf_conversation()
                tunggu()

            elif pilihan == "5":
                print("\nAplikasi ditutup.")
                break

            else:
                print("\nPilihan tidak valid. Pilih angka 1 sampai 5.")
                tunggu()

        except KeyboardInterrupt:
            print("\n\nProses dibatalkan oleh pengguna.")
            tunggu()

        except Exception as error:
            print(f"\nTerjadi kesalahan: {error}")
            tunggu()


if __name__ == "__main__":
    main()
