# Transkrip Meeting — Plugin Hermes

Plugin Hermes untuk merekam atau mengimpor audio meeting, membuat transkrip lokal dalam format PDF, menganalisisnya melalui provider aktif Hermes, serta mengekspor hasil analisis ke TXT, PDF, dan DOCX.

## Persyaratan

- Windows 10/11.
- Hermes Agent sudah terpasang dan dapat dipanggil dengan perintah `hermes`.
- Provider/model Hermes sudah aktif.
- Koneksi internet untuk instalasi plugin dan analisis melalui Hermes.
- Mikrofon dan speaker diperlukan hanya untuk perekaman langsung.

FFmpeg dan dependensi Python plugin dipasang atau disediakan bersama plugin; pengguna tidak perlu memasangnya satu per satu.

## Instalasi

Jalankan satu perintah berikut di terminal:

```bash
hermes plugins install ramfdp/Ai-backgroun-python-meeting --enable
```

Perintah tersebut akan:

1. Mengunduh plugin dari GitHub.
2. Mengaktifkan plugin secara otomatis.
3. Menambahkan perintah `/transkrip` ke Hermes.

Setelah instalasi, tutup dan buka kembali Hermes. Pada sesi baru, plugin otomatis memeriksa seluruh dependency di `requirements.txt`. Dependency yang belum tersedia akan dipasang ke environment Python Hermes sebelum `/transkrip` digunakan.

Tunggu sampai muncul:

```text
[transkrip-meeting] Instalasi selesai. /transkrip siap digunakan.
```

Jika seluruh dependency sudah tersedia, pemeriksaan dilewati sehingga startup berikutnya tidak mengunduh ulang paket.

### Cara kerja pemasangan dependency

- Plugin memeriksa modul yang diperlukan saat diregistrasikan pada sesi Hermes baru.
- Jika ada yang belum tersedia, plugin menjalankan `uv pip install` terhadap Python environment yang sedang menjalankan Hermes.
- Jika `uv` tidak ditemukan, plugin mencoba fallback `ensurepip` dan `pip`.
- Instalasi wajib selesai dan seluruh modul wajib dapat ditemukan sebelum fitur transkrip diizinkan berjalan.
- Kegagalan disimpan sebagai status plugin dan ditampilkan melalui `/transkrip`; fitur tidak dijalankan dalam kondisi setengah terpasang.

## Verifikasi instalasi

```bash
hermes plugins list --user
```

Pastikan `transkrip-meeting` tampil dalam keadaan `enabled`.

## Cara penggunaan

Buka Hermes, kemudian tampilkan menu plugin:

```text
/transkrip
```

Jika instalasi dependency berhasil, menu diawali pesan `Plugin transkrip siap digunakan`. Jika gagal, `/transkrip` menampilkan penyebabnya dan tidak menjalankan fitur yang belum siap.

### Pilihan 1 — Rekam meeting langsung

```text
/transkrip 1
```

Hermes membuka jendela CMD dan merekam suara mikrofon serta speaker. Tekan `ESC` atau `Ctrl+C` pada jendela tersebut untuk menghentikan perekaman. Audio kemudian ditranskripsikan secara lokal dan dianalisis menggunakan provider aktif Hermes.

### Pilihan 2 — Impor file audio

```text
/transkrip 2
```

Pilih file `.wav`, `.mp3`, atau `.m4a`. Plugin menyalin audio ke folder penyimpanan, membuat transkrip lokal dalam format PDF, lalu menghasilkan analisis melalui Hermes.

### Pilihan 3 — Reduksi noise dan buat notulensi

```text
/transkrip 3
```

Pilih file `.wav`, `.mp3`, `.m4a`, `.flac`, atau `.ogg`. Plugin akan:

1. Mengubah audio menjadi mono 16 kHz.
2. Mengurangi background noise.
3. Menerapkan filter vokal dan normalisasi.
4. Menyimpan MP3 hasil tuning.
5. Meneruskan hasilnya ke pipeline transkripsi dan analisis Hermes yang sama dengan pilihan 1–2.

### Pilihan 4 — Analisis percakapan dari PDF

```text
/transkrip 4
```

Pilih PDF hasil transkrip yang memiliki percakapan bertimestamp. PDF dari pilihan 1, 2, atau 3 dapat langsung digunakan pada pilihan ini. Plugin mengekstrak percakapan ke PDF baru, menganalisisnya melalui provider aktif Hermes, lalu membuat hasil analisis TXT, PDF, dan DOCX.

### Pilihan 5 — Batalkan operasi

```text
/transkrip 5
```

Operasi transkrip dibatalkan tanpa membuka proses lain atau membuat file.

## Lokasi hasil

Semua hasil disimpan di:

```text
Desktop\Hermes Transkrip\
├── Rekaman\
├── Hasil Tuning\
├── Transkrip\
└── Analisis Lengkap\
```

- `Rekaman`: audio hasil rekaman atau impor.
- `Hasil Tuning`: audio pilihan 3 setelah reduksi noise.
- `Transkrip`: seluruh hasil transkripsi dan ekstraksi percakapan dalam format PDF; hasil pilihan 1–3 dapat digunakan langsung pada pilihan 4.
- `Analisis Lengkap`: hasil analisis dalam format TXT, PDF, dan DOCX.

## Memperbarui plugin

```bash
hermes plugins update transkrip-meeting
```

Buka kembali Hermes setelah pembaruan selesai.

## Menonaktifkan atau menghapus plugin

Nonaktifkan tanpa menghapus:

```bash
hermes plugins disable transkrip-meeting
```

Aktifkan kembali:

```bash
hermes plugins enable transkrip-meeting
```

Hapus plugin:

```bash
hermes plugins uninstall transkrip-meeting
```

## Penanganan masalah

### `/transkrip` tidak ditemukan

1. Pastikan plugin terpasang dan aktif:

   ```bash
   hermes plugins list --user
   ```

2. Jika statusnya belum aktif:

   ```bash
   hermes plugins enable transkrip-meeting
   ```

3. Tutup seluruh sesi Hermes, lalu buka sesi baru.

### Muncul `Plugin transkrip belum siap`

Pesan tersebut berarti instalasi dependency gagal atau belum lengkap. Pastikan koneksi internet aktif dan ruang disk tersedia, tutup seluruh sesi Hermes, lalu jalankan:

```bash
hermes doctor --fix
hermes plugins update transkrip-meeting
```

Buka Hermes kembali dan tunggu pemeriksaan dependency selesai. Jalankan `/transkrip` untuk melihat status terbaru.

### Update tidak memperbaiki dependency

Lakukan instalasi ulang bersih:

```bash
hermes plugins install ramfdp/Ai-backgroun-python-meeting --force --enable
```

Kemudian buka sesi Hermes baru. File hasil meeting di `Desktop\Hermes Transkrip` tidak berada di folder instalasi plugin sehingga tidak ikut terhapus saat reinstall.

### Instalasi berhenti saat mengunduh paket

- Pastikan firewall/proxy mengizinkan akses GitHub, PyPI, dan Hugging Face.
- Jangan tutup Hermes selama proses instalasi berlangsung.
- Model Whisper lokal diunduh saat pertama kali audio ditranskripsikan; proses pertama dapat lebih lama.
- Jika muncul masalah file sedang digunakan atau permission denied, tutup seluruh proses Hermes lalu ulangi reinstall dari terminal yang memiliki hak tulis ke folder pengguna.

### Perekaman langsung tidak menangkap suara

- Pastikan Windows mengizinkan akses mikrofon untuk aplikasi desktop.
- Pastikan mikrofon dan speaker default sudah benar.
- Gunakan pilihan 2 untuk menguji pipeline dengan file audio yang sudah tersedia.

### Audio pilihan 2 atau 3 gagal dibaca

- Pastikan ekstensi sesuai format yang didukung.
- Pastikan file tidak rusak dan tidak sedang dikunci aplikasi lain.
- Pilihan 2 menerima `.wav`, `.mp3`, dan `.m4a`.
- Pilihan 3 menerima `.wav`, `.mp3`, `.m4a`, `.flac`, dan `.ogg`.

### Analisis Hermes gagal

Pastikan provider/model Hermes aktif dan dapat digunakan:

```bash
hermes status --all
hermes doctor
```

Transkrip atau rekaman yang sudah berhasil dibuat tetap disimpan meskipun tahap analisis gagal.

### Melihat error Hermes

```bash
hermes logs errors
```

Pemeriksaan umum:

```bash
hermes plugins list --user
hermes doctor
```

Jika `/transkrip` belum tersedia setelah instalasi atau pembaruan, tutup seluruh sesi Hermes lalu buka kembali.
