$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$python = (Get-Command python -ErrorAction Stop).Source
& $python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host 'Dependencies installed.'
Write-Host 'Run Run-Overlay.vbs to start the app.'
