$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & .\Install-Dependencies.ps1
}
else {
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

& .\.venv\Scripts\python.exe -m pip install --force-reinstall "setuptools<81" "pyinstaller==5.13.2" "pyinstaller-hooks-contrib<2025"
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to install PyInstaller.'
}

& .\.venv\Scripts\python.exe -m PyInstaller `
    --clean `
    --noconsole `
    --onefile `
    --name ForzaMusicOverlay `
    --collect-submodules winsdk `
    --collect-data pygame `
    --hidden-import pygame `
    .\forza_music_overlay.py
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller build failed.'
}

Write-Host 'Build complete:'
Write-Host (Join-Path $scriptDir 'dist\ForzaMusicOverlay.exe')
