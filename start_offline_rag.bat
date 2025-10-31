@echo off
title Offline RAG Launcher
echo Starting Ollama, backend, and frontend...
REM Make sure ollama is installed and model pulled

start cmd /k "ollama serve"
timeout /t 4 >nul

cd backend
start cmd /k "python main.py"
cd ..

cd frontend
start cmd /k "node app.js"
cd ..
echo All started.
pause
