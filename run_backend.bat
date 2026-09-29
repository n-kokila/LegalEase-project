@echo off
setlocal enabledelayedexpansion

for /f "tokens=1" %%A in ('python find_ports.py backend') do (
    set BACKEND_PORT=%%A
)
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000

echo ========================================================
echo Starting LegalEase Backend on http://127.0.0.1:%BACKEND_PORT% ...
echo Swagger Docs: http://127.0.0.1:%BACKEND_PORT%/docs
echo ========================================================

python -m uvicorn main:app --reload --port %BACKEND_PORT%
pause
