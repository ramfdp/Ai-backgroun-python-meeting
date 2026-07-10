@echo off
title AI Meeting Notulensi
color 0A

:menu
cls
echo          SISTEM AI NOTULENSI MEETING v1.5
echo ==================================================
echo 1.  Mulai Rekam Meeting (Live AI)
echo 2.  Upload File Audio (.wav/.mp3/.m4a) Manual
echo 3.  Keluar Aplikasi
echo ==================================================
echo.
set /p pilihan="Masukkan angka pilihan Anda (1/2/3): "

if "%pilihan%"=="1" (
    .venv\Scripts\python.exe main.py
    pause
    goto menu
)
if "%pilihan%"=="2" (
    .venv\Scripts\python.exe upload.py
    pause
    goto menu
)
if "%pilihan%"=="3" exit

goto menu
