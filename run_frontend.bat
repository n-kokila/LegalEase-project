@echo off
setlocal enabledelayedexpansion

:: Check if backend port was saved from a running backend
set BACKEND_PORT=8000
if exist .backend_port (
    set /p BACKEND_PORT=<.backend_port
)
set BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%

for /f "tokens=1" %%A in ('python find_ports.py frontend') do (
    set FRONTEND_PORT=%%A
)
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=8501

echo ========================================================
echo Starting LegalEase Streamlit App on http://localhost:%FRONTEND_PORT% ...
echo Backend target: %BACKEND_URL%
echo ========================================================

python -m streamlit run app.py --server.port %FRONTEND_PORT% --browser.gatherUsageStats false
pause
