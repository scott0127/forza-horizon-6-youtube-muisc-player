$ErrorActionPreference = 'Stop'

$installDir = Join-Path $env:LOCALAPPDATA 'Programs\ForzaMusicOverlay'

function ConvertFrom-Utf8Base64 {
    param([string]$Value)
    return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Value))
}

# Keep this script ASCII-safe for Windows PowerShell 5.1, which may read UTF-8
# files without a BOM as the system ANSI code page.
$appShortcutName = ConvertFrom-Utf8Base64 'Rm9yemEg6Z+z5qiC5oe45rWu5pKt5pS+5Zmo'
$desktopShortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) "$appShortcutName.lnk"
$legacyDesktopShortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Forza Music Overlay.lnk'
$startMenu = Join-Path ([Environment]::GetFolderPath('Programs')) $appShortcutName
$legacyStartMenu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Forza Music Overlay'

Get-CimInstance Win32_Process |
    Where-Object {
        ($_.Name -eq 'ForzaMusicOverlayBackend.exe' -or $_.Name -eq 'ForzaMusicOverlayApp.exe' -or $_.Name -eq 'ForzaMusicOverlay.exe' -or $_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and
        $_.CommandLine -and
        $_.CommandLine.Contains('ForzaMusicOverlay')
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

if (Test-Path -LiteralPath $desktopShortcut) {
    Remove-Item -LiteralPath $desktopShortcut -Force
}

if (Test-Path -LiteralPath $legacyDesktopShortcut) {
    Remove-Item -LiteralPath $legacyDesktopShortcut -Force
}

if (Test-Path -LiteralPath $startMenu) {
    Remove-Item -LiteralPath $startMenu -Recurse -Force
}

if (Test-Path -LiteralPath $legacyStartMenu) {
    Remove-Item -LiteralPath $legacyStartMenu -Recurse -Force
}

if (Test-Path -LiteralPath $installDir) {
    Remove-Item -LiteralPath $installDir -Recurse -Force
}

Write-Host "$appShortcutName uninstalled."
Write-Host 'User settings were kept in %LOCALAPPDATA%\ForzaMusicOverlay.'
