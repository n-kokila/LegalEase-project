@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo Starting LegalEase - AI-Powered Legal Document Generator
echo ========================================================
echo Generating new dynamic localhost ports for this run...

:: Allocate available random ports for backend and frontend
for /f "tokens=1,2" %%A in ('python find_ports.py both') do (
    set BACKEND_PORT=%%A
    set FRONTEND_PORT=%%B
)

if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=8501

set BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%

echo.
echo [Dynamic Ports Allocated]
echo   - Backend (FastAPI)   : http://127.0.0.1:%BACKEND_PORT%
echo   - API Documentation   : http://127.0.0.1:%BACKEND_PORT%/docs
echo   - Frontend (Streamlit): http://localhost:%FRONTEND_PORT%
echo ========================================================

echo 1. Launching FastAPI Backend on http://127.0.0.1:%BACKEND_PORT% ...
start "LegalEase Backend (%BACKEND_PORT%)" cmd /k "set BACKEND_PORT=%BACKEND_PORT% && python -m uvicorn main:app --reload --port %BACKEND_PORT%"

echo 2. Waiting 3 seconds for backend initialization...
ping 127.0.0.1 -n 4 >nul

echo 3. Launching Streamlit Frontend on http://localhost:%FRONTEND_PORT% ...
start "LegalEase Frontend (%FRONTEND_PORT%)" cmd /k "set BACKEND_URL=%BACKEND_URL% && python -m streamlit run app.py --server.port %FRONTEND_PORT% --browser.gatherUsageStats false"

echo.
echo All services launched!
echo Streamlit will automatically open http://localhost:%FRONTEND_PORT% in your browser.
echo ========================================================
