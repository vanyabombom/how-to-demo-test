@echo off
echo Starting Demo2HowTo Services...

start "Backend - FastAPI" cmd /k "cd /d %~dp0backend && py -3.13 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

start "Frontend - Vite React" cmd /k "cd /d %~dp0frontend && npm run dev"

echo =======================================================
echo Demo2HowTo is launching!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo =======================================================
