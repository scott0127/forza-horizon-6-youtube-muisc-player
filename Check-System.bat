@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXE=.venv\Scripts\python.exe
) else (
  set PYTHON_EXE=python
)

%PYTHON_EXE% forza_music_overlay.py --check
%PYTHON_EXE% forza_music_overlay.py --hotkey-check
%PYTHON_EXE% forza_music_overlay.py --once
pause
