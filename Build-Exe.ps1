$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'

if (Test-Path -LiteralPath $venvPython) {
    $venvVersion = & $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if ($LASTEXITCODE -ne 0 -or [version]$venvVersion -ne [version]'3.12') {
        Write-Host 'Existing .venv is not Python 3.12. Recreating it.'
        Remove-Item -LiteralPath (Join-Path $scriptDir '.venv') -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    & .\Install-Dependencies.ps1
}
else {
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to install dependencies.'
    }
}

& $venvPython -m pip install --force-reinstall "setuptools<81" "pyinstaller>=6.14,<7" "pyinstaller-hooks-contrib>=2025.8"
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to install PyInstaller.'
}

& $venvPython -m PyInstaller `
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
