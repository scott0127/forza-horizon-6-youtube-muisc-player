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
$appShortcutName = 'Forza 音樂懸浮播放器'
$startMenu = Join-Path ([Environment]::GetFolderPath('Programs')) $appShortcutName
$legacyDesktopShortcut = Join-Path $desktop 'Forza Music Overlay.lnk'
$legacyStartMenu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Forza Music Overlay'

if (Test-Path -LiteralPath $legacyDesktopShortcut) {
    Remove-Item -LiteralPath $legacyDesktopShortcut -Force
}

if (Test-Path -LiteralPath $legacyStartMenu) {
    Remove-Item -LiteralPath $legacyStartMenu -Recurse -Force
}

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
    $shortcut.Description = $appShortcutName
    $shortcut.Save()
}

New-AppShortcut -Path (Join-Path $desktop "$appShortcutName.lnk")
New-AppShortcut -Path (Join-Path $startMenu "$appShortcutName.lnk")
New-AppShortcut -Path (Join-Path $startMenu "$appShortcutName - 只顯示播放器.lnk") -Arguments '--overlay-only'

$uninstallerSource = Join-Path $sourceDir 'Uninstall-App.ps1'
if (Test-Path -LiteralPath $uninstallerSource) {
    Copy-Item -LiteralPath $uninstallerSource -Destination (Join-Path $installDir 'Uninstall-App.ps1') -Force

    $shortcut = $shell.CreateShortcut((Join-Path $startMenu "解除安裝 $appShortcutName.lnk"))
    $shortcut.TargetPath = 'powershell.exe'
    $shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $installDir 'Uninstall-App.ps1') + '"'
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Description = "解除安裝 $appShortcutName"
    $shortcut.Save()
}

Write-Host ''
Write-Host "$appShortcutName installed."
Write-Host "Install path: $installDir"
Write-Host 'Desktop and Start Menu shortcuts were created.'
