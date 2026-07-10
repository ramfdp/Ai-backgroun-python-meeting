@echo off
title AI Meeting Notulensi
color 0A

echo Menyiapkan Sistem...
echo.

:: Menjalankan script python utama
.venv\Scripts\python.exe main.py

echo.
:: Pause digunakan agar jendela CMD tidak langsung hilang setelah proses PDF selesai, 
:: sehingga Anda bisa membaca lokasi folder tempat PDF disimpan.
pause