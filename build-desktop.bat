@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Please create .venv and install requirements-desktop.txt first.
    exit /b 1
)
.venv\Scripts\python.exe tools\check_backend.py || exit /b 1
.venv\Scripts\python.exe test_ui.py || exit /b 1
.venv\Scripts\python.exe test_cli.py || exit /b 1
.venv\Scripts\python.exe test_product.py || exit /b 1
.venv\Scripts\python.exe test_reshade_ini.py || exit /b 1
REM Avoid collecting unrelated ICU / API-set DLLs from tools on the host PATH.
set "PATH=%~dp0.venv\Scripts;%SystemRoot%\System32;%SystemRoot%"
.venv\Scripts\python.exe tools\build_desktop.py || exit /b 1
.venv\Scripts\python.exe tools\smoke_desktop.py
exit /b %errorlevel%
