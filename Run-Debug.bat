@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" forza_music_overlay.py
) else (
  python forza_music_overlay.py
)
