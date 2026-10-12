@echo off
echo ============================================================
echo   Starting TravelPulse Enterprise Platform (Agoda Rebuild)
echo ============================================================
echo.
echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "TravelPulse FastAPI Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting React Vite Frontend on http://localhost:5173 ...
start "TravelPulse React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both services launched!
echo - Backend API:  http://localhost:8000/docs
echo - Frontend App: http://localhost:5173
echo ============================================================
