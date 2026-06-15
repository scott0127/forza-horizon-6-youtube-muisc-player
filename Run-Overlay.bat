@echo off
setlocal
cd /d "%~dp0"

if not exist ".\.venv\Scripts\python.exe" (
  echo Missing .venv. Run Install-Dependencies.bat first.
  pause
  exit /b 1
)

".\.venv\Scripts\python.exe" ".\forza_music_overlay.py" %*
pause
