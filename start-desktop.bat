@echo off
setlocal
set "app=%~dp0dist\v0.2.1\JustDLSS5\JustDLSS5.exe"
if not exist "%app%" (
    echo JustDLSS5 has not been built. Run build-desktop.bat first.
    pause
    exit /b 1
)
start "" "%app%"
