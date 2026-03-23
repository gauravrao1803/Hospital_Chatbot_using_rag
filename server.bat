@echo off
title AI Server Launcher

echo =====================================
echo   Starting AI Chatbot Server...
echo =====================================
timeout /t 2

cd /d "C:\Users\gaura\Music\Hospital Chatbot"

echo.
echo 🔹 Starting FastAPI Server...
start cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo Waiting for server to initialize...
timeout /t 5

echo.
echo 🔹 Starting ngrok Tunnel...
start cmd /k "ngrok http 8000"

echo.
echo ✅ AI Server and Ngrok Started Successfully!
pause