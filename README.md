# Transkrip Meeting — Plugin Hermes

Plugin Hermes untuk merekam atau mengimpor audio meeting, membuat transkrip lokal, menganalisisnya melalui provider aktif Hermes, serta mengekspor hasil ke TXT, PDF, dan DOCX.

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
2. Memasang dependensi yang tercantum di `plugin.yaml`.
3. Mengaktifkan plugin secara otomatis.
4. Menambahkan perintah `/transkrip` ke Hermes.

Setelah selesai, tutup dan buka kembali Hermes agar plugin dimuat pada sesi baru.

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

### Pilihan 1 — Rekam meeting langsung

```text
/transkrip 1
```

Hermes membuka jendela CMD dan merekam suara mikrofon serta speaker. Tekan `ESC` atau `Ctrl+C` pada jendela tersebut untuk menghentikan perekaman. Audio kemudian ditranskripsikan secara lokal dan dianalisis menggunakan provider aktif Hermes.

### Pilihan 2 — Impor file audio

```text
/transkrip 2
```

Pilih file `.wav`, `.mp3`, atau `.m4a`. Plugin menyalin audio ke folder penyimpanan, membuat transkrip lokal, lalu menghasilkan analisis melalui Hermes.

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

Pilih PDF hasil transkrip yang memiliki percakapan bertimestamp. Plugin mengekstrak percakapan, menganalisisnya melalui provider aktif Hermes, lalu membuat hasil TXT, PDF, dan DOCX.

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
- `Transkrip`: hasil transkripsi dalam format TXT.
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

## Pemecahan masalah singkat

Periksa apakah plugin aktif:

```bash
hermes plugins list --user
```

Periksa kondisi Hermes:

```bash
hermes doctor
```

Jika `/transkrip` belum tersedia setelah instalasi atau pembaruan, tutup seluruh sesi Hermes lalu buka kembali.
