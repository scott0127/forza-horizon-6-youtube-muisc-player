$ErrorActionPreference = 'Stop'

$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exeSource = Join-Path $sourceDir 'ForzaMusicOverlay.exe'

if (-not (Test-Path -LiteralPath $exeSource)) {
    throw "ForzaMusicOverlay.exe was not found next to this installer."
}

$installDir = Join-Path $env:LOCALAPPDATA 'Programs\ForzaMusicOverlay'
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Copy-Item -LiteralPath $exeSource -Destination (Join-Path $installDir 'ForzaMusicOverlay.exe') -Force

$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$startMenu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Forza Music Overlay'
New-Item -ItemType Directory -Force -Path $startMenu | Out-Null

function New-AppShortcut {
    param(
        [string]$Path,
        [string]$Arguments = ''
    )

    $shortcut = $shell.CreateShortcut($Path)
    $shortcut.TargetPath = Join-Path $installDir 'ForzaMusicOverlay.exe'
    $shortcut.Arguments = $Arguments
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Description = 'Forza Music Overlay'
    $shortcut.Save()
}

New-AppShortcut -Path (Join-Path $desktop 'Forza Music Overlay.lnk')
New-AppShortcut -Path (Join-Path $startMenu 'Forza Music Overlay.lnk')
New-AppShortcut -Path (Join-Path $startMenu 'Forza Music Overlay - Overlay Only.lnk') -Arguments '--overlay-only'

$uninstallerSource = Join-Path $sourceDir 'Uninstall-App.ps1'
if (Test-Path -LiteralPath $uninstallerSource) {
    Copy-Item -LiteralPath $uninstallerSource -Destination (Join-Path $installDir 'Uninstall-App.ps1') -Force

    $shortcut = $shell.CreateShortcut((Join-Path $startMenu 'Uninstall Forza Music Overlay.lnk'))
    $shortcut.TargetPath = 'powershell.exe'
    $shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $installDir 'Uninstall-App.ps1') + '"'
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Description = 'Uninstall Forza Music Overlay'
    $shortcut.Save()
}

Write-Host ''
Write-Host 'Forza Music Overlay installed.'
Write-Host "Install path: $installDir"
Write-Host 'Desktop and Start Menu shortcuts were created.'
