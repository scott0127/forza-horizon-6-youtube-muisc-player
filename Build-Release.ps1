$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

& .\Build-Exe.ps1

$releaseRoot = Join-Path $scriptDir 'release'
$packageDir = Join-Path $releaseRoot 'ForzaMusicOverlay'
$zipPath = Join-Path $releaseRoot 'ForzaMusicOverlay.zip'

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -LiteralPath $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null

Copy-Item -LiteralPath '.\dist\ForzaMusicOverlay.exe' -Destination (Join-Path $packageDir 'ForzaMusicOverlay.exe') -Force
Copy-Item -LiteralPath '.\release-assets\Install-App.ps1' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\release-assets\Install-App.bat' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\release-assets\Uninstall-App.ps1' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\release-assets\Uninstall-App.bat' -Destination $packageDir -Force
Copy-Item -LiteralPath '.\README.md' -Destination (Join-Path $packageDir 'README.md') -Force
Copy-Item -LiteralPath '.\README.txt' -Destination (Join-Path $packageDir 'README.txt') -Force
Copy-Item -LiteralPath '.\Install-Guide.png' -Destination (Join-Path $packageDir 'Install-Guide.png') -Force

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -LiteralPath $packageDir -DestinationPath $zipPath -Force

Write-Host ''
Write-Host 'Release package created:'
Write-Host $zipPath
