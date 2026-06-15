@echo off
setlocal
cd /d "%~dp0"
set "SOURCE_DIR=%~dp0"
if "%SOURCE_DIR:~-1%"=="\" set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"
powershell.exe -NoProfile -File ".\AppFiles\Install-App.ps1" -SourceDir "%SOURCE_DIR%"
pause
