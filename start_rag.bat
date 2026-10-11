@echo off
title RAG-Polri Launcher
echo ============================================
echo   RAG-POLRI CHATBOT
echo   Seleksi Tahap 2 - BAGINFOPERS ROBNIKAR
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Memeriksa Python...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 tidak ditemukan!
    pause
    exit /b 1
)

echo [2/3] Menjalankan API (port 8000)...
start "RAG-Polri API" cmd /k "cd /d %~dp0 && py -3.12 -m uvicorn api.main:app --port 8000"

timeout /t 3 /nobreak >nul

echo [3/3] Menjalankan Streamlit (port 8501)...
start "RAG-Polri UI" cmd /k "cd /d %~dp0 && py -3.12 -m streamlit run app.py"

timeout /t 8 /nobreak >nul

echo.
echo ============================================
echo   Aplikasi berjalan!
echo   - Chat UI: http://localhost:8501
echo   - API Docs: http://localhost:8000/docs
echo ============================================
echo.
echo Browser akan terbuka otomatis...
start http://localhost:8501

echo.
echo Tekan tombol apa saja untuk keluar dari launcher ini.
echo (Aplikasi tetap berjalan di 2 jendela yang terbuka)
pause >nul