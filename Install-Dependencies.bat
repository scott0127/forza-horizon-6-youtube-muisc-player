@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -File ".\Install-Dependencies.ps1"
pause
