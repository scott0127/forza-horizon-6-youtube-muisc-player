@echo off
setlocal
cd /d "%~dp0"
if exist ".\AppFiles\Uninstall-App.ps1" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\AppFiles\Uninstall-App.ps1"
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\Uninstall-App.ps1"
)
pause
