@echo off
setlocal
cd /d "%~dp0"
if exist ".\AppFiles\Uninstall-App.ps1" (
  powershell.exe -NoProfile -File ".\AppFiles\Uninstall-App.ps1"
) else (
  powershell.exe -NoProfile -File ".\Uninstall-App.ps1"
)
pause
