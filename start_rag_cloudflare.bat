@echo off
title RAG-Polri Public Launcher (Cloudflare)
color 0B
cd /d "%~dp0"

echo ====================================================
echo    RAG-POLRI - PUBLIC LAUNCHER
echo    (Akses dari Internet via Cloudflare Tunnel)
echo ====================================================
echo.

echo [1/2] Menjalankan Streamlit...
start "RAG-Polri UI" cmd /k "cd /d %~dp0 && py -3.12 -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501"
timeout /t 8 /nobreak >nul

echo [2/2] Membuka Cloudflare Tunnel...
start "RAG-Polri Cloudflare" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --url http://localhost:8501 > public_url.txt 2>&1"

echo.
echo Menunggu URL publik dibuat...
timeout /t 15 /nobreak >nul

echo.
echo ====================================================
echo    URL PUBLIK ANDA:
echo ====================================================
findstr /C:"trycloudflare.com" public_url.txt
echo ====================================================
echo.
echo URL juga tersimpan di: public_url.txt
pause >nul