param(
    [string]$SourceDir = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    $sourceDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
else {
    $sourceDir = $SourceDir.Trim().Trim('"')
}

$sourceDir = $sourceDir.TrimEnd('\', '/')
$sourceDir = (Resolve-Path -LiteralPath $sourceDir).Path
$exeSource = Join-Path $sourceDir 'ForzaMusicOverlay.exe'
$appFilesSource = Join-Path $sourceDir 'AppFiles'

if (-not (Test-Path -LiteralPath $exeSource)) {
    throw "ForzaMusicOverlay.exe was not found next to this installer."
}

if (-not (Test-Path -LiteralPath $appFilesSource)) {
    throw "AppFiles was not found next to this installer."
}

$installDir = Join-Path $env:LOCALAPPDATA 'Programs\ForzaMusicOverlay'
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

Get-ChildItem -LiteralPath $sourceDir -Force |
    Where-Object { $_.Name -notin @('Install-App.bat') } |
    ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $installDir -Recurse -Force
    }

$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')

function ConvertFrom-Utf8Base64 {
    param([string]$Value)
    return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Value))
}

# English version: use plain ASCII names
$appShortcutName = 'Forza Music Floating Player'
$overlayOnlySuffix = ' - Overlay Only'
$uninstallPrefix = 'Uninstall '
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

$shortcutIcon = Join-Path $installDir 'AppFiles\resources\app-assets\logo.ico'
if (-not (Test-Path -LiteralPath $shortcutIcon)) {
    $shortcutIcon = Join-Path $installDir 'ForzaMusicOverlay.exe'
}

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
    $shortcut.IconLocation = "$shortcutIcon,0"
    $shortcut.Save()
}

New-AppShortcut -Path (Join-Path $desktop "$appShortcutName.lnk")
New-AppShortcut -Path (Join-Path $startMenu "$appShortcutName.lnk")
New-AppShortcut -Path (Join-Path $startMenu "$appShortcutName$overlayOnlySuffix.lnk") -Arguments '--overlay-only'

$uninstallerSource = Join-Path $installDir 'AppFiles\Uninstall-App.ps1'
if (Test-Path -LiteralPath $uninstallerSource) {
    $shortcut = $shell.CreateShortcut((Join-Path $startMenu "$uninstallPrefix$appShortcutName.lnk"))
    $shortcut.TargetPath = 'powershell.exe'
    $shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $uninstallerSource + '"'
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Description = "$uninstallPrefix$appShortcutName"
    $shortcut.IconLocation = "$shortcutIcon,0"
    $shortcut.Save()
}

Write-Host ''
Write-Host "$appShortcutName installed."
Write-Host "Install path: $installDir"
Write-Host 'Desktop and Start Menu shortcuts were created.'
