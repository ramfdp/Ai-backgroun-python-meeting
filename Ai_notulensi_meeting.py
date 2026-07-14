import os

from main import main as jalankan_rekaman
from upload import upload_audio as jalankan_upload
from audio_compressor import main as jalankan_kompresi


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


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
        print("4. Keluar Aplikasi")
        print("=" * 65)

        pilihan = input("\nMasukkan angka pilihan Anda (1/2/3/4): ").strip()

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
                print("\nAplikasi ditutup.")
                break

            else:
                print("\nPilihan tidak valid. Pilih angka 1 sampai 4.")
                tunggu()

        except KeyboardInterrupt:
            print("\n\nProses dibatalkan oleh pengguna.")
            tunggu()

        except Exception as error:
            print(f"\nTerjadi kesalahan: {error}")
            tunggu()


if __name__ == "__main__":
    main()