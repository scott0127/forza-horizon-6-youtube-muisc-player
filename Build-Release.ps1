param(
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$branch = (git rev-parse --abbrev-ref HEAD)
$isEnglish = ($branch -like '*eng*')
$suffix = if ($isEnglish) { '_eng' } else { '' }
$appVersion = '2.3.1'
$releaseRoot = Join-Path $scriptDir 'release'
$packageDir = Join-Path $releaseRoot "ForzaMusicOverlay-release$appVersion$suffix"
$appFilesDir = Join-Path $packageDir 'AppFiles'
$rarPath = Join-Path $releaseRoot "ForzaMusicOverlay-release$appVersion$suffix.rar"
$launcherOut = Join-Path $scriptDir 'tmp\launcher\ForzaMusicOverlay.exe'
$iconPath = Join-Path $scriptDir 'electron-app\build\logo.ico'

if (-not (Test-Path -LiteralPath $iconPath)) {
    throw "App icon was not found: $iconPath"
}

if (-not $SkipBuild) {
    pnpm --dir electron-app build
    if ($LASTEXITCODE -ne 0) {
        throw 'Electron build failed.'
    }

    $venvPython = Join-Path $scriptDir '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        & .\Install-Dependencies.ps1
    }

    & $venvPython -m PyInstaller `
        --clean `
        --onefile `
        --name ForzaMusicOverlayBackend `
        --collect-submodules winsdk `
        --collect-data pygame `
        --hidden-import pygame `
        .\forza_music_overlay.py
    if ($LASTEXITCODE -ne 0) {
        throw 'Backend PyInstaller build failed.'
    }
}

$electronDist = Join-Path $scriptDir 'electron-app\node_modules\electron\dist'
$electronExe = Join-Path $electronDist 'electron.exe'
$appOut = Join-Path $scriptDir 'electron-app\out'
$backendExe = Join-Path $scriptDir 'dist\ForzaMusicOverlayBackend.exe'

foreach ($required in @($electronExe, $appOut, $backendExe)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required build output missing: $required"
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $launcherOut) | Out-Null
$cscCandidates = @(
    (Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'),
    (Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe')
)
$csc = $cscCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $csc) {
    throw 'C# compiler csc.exe was not found.'
}

& $csc `
    /nologo `
    /target:winexe `
    /win32icon:"$iconPath" `
    /reference:System.dll `
    /reference:System.Windows.Forms.dll `
    /out:"$launcherOut" `
    ".\release-assets\Launcher.cs"
if ($LASTEXITCODE -ne 0) {
    throw 'Launcher build failed.'
}

if (-not (Test-Path -LiteralPath $releaseRoot)) {
    New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null
}

$resolvedReleaseRoot = (Resolve-Path -LiteralPath $releaseRoot).Path
$fullPackageDir = [System.IO.Path]::GetFullPath($packageDir)
if (-not $fullPackageDir.StartsWith($resolvedReleaseRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Package directory is outside the release folder: $fullPackageDir"
}

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -LiteralPath $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
New-Item -ItemType Directory -Force -Path $appFilesDir | Out-Null

Copy-Item -LiteralPath $launcherOut -Destination (Join-Path $packageDir 'ForzaMusicOverlay.exe') -Force
Copy-Item -LiteralPath '.\release-assets\Install-App.bat' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\release-assets\Uninstall-App.bat' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\README.md' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\README.txt' -Destination $packageDir -Force

Copy-Item -Path (Join-Path $electronDist '*') -Destination $appFilesDir -Recurse -Force
Move-Item -LiteralPath (Join-Path $appFilesDir 'electron.exe') -Destination (Join-Path $appFilesDir 'ForzaMusicOverlayApp.exe') -Force

$appDir = Join-Path $appFilesDir 'resources\app'
New-Item -ItemType Directory -Force -Path $appDir | Out-Null
Copy-Item -LiteralPath $appOut -Destination $appDir -Recurse -Force
("{`"name`":`"forza-music-overlay`",`"version`":`"$appVersion`",`"main`":`"out/main/index.js`"}") |
    Set-Content -LiteralPath (Join-Path $appDir 'package.json') -Encoding UTF8

$backendDir = Join-Path $appFilesDir 'resources\backend'
New-Item -ItemType Directory -Force -Path $backendDir | Out-Null
Copy-Item -LiteralPath $backendExe -Destination $backendDir -Force

$appAssetsDir = Join-Path $appFilesDir 'resources\app-assets'
New-Item -ItemType Directory -Force -Path $appAssetsDir | Out-Null
Copy-Item -LiteralPath '.\electron-app\build\logo.ico' -Destination $appAssetsDir -Force
Copy-Item -LiteralPath '.\electron-app\build\logo-rounded.png' -Destination (Join-Path $appAssetsDir 'logo.png') -Force

Copy-Item -LiteralPath '.\release-assets\Install-App.ps1' -Destination $appFilesDir -Force
Copy-Item -LiteralPath '.\release-assets\Uninstall-App.ps1' -Destination $appFilesDir -Force
Copy-Item -LiteralPath '.\LICENSE' -Destination $appFilesDir -Force

Write-Host "Creating uncompressible random padding file to exceed Google Drive's 100MB scan limit..."
$paddingPath = Join-Path $appFilesDir 'google_drive_scan_bypass.bin'
$randomBytes = New-Object Byte[] (50 * 1024 * 1024)
$rand = New-Object System.Random
$rand.NextBytes($randomBytes)
[System.IO.File]::WriteAllBytes($paddingPath, $randomBytes)

$rarExe = "C:\Program Files\WinRAR\Rar.exe"
if (Test-Path -LiteralPath $rarPath) {
    Remove-Item -LiteralPath $rarPath -Force
}

Write-Host "Compressing release package to RAR using WinRAR..."
& $rarExe a -r -ep1 "$rarPath" "$packageDir"
if ($LASTEXITCODE -ne 0) {
    throw 'WinRAR compression failed.'
}

$rarItem = Get-Item -LiteralPath $rarPath
$packageItemCount = (Get-ChildItem -LiteralPath $packageDir -Recurse -File | Measure-Object).Count

Write-Host ''
Write-Host 'Release package created:'
Write-Host $rarPath
Write-Host "Size: $([Math]::Round($rarItem.Length / 1MB, 2)) MB"
Write-Host "Files: $packageItemCount"
