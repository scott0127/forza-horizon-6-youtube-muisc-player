$ErrorActionPreference = 'Stop'

$scriptName = 'forza_music_overlay.py'
$processes = Get-CimInstance Win32_Process |
    Where-Object {
        ($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and
        $_.CommandLine -and
        $_.CommandLine.Contains($scriptName)
    }

foreach ($process in $processes) {
    Stop-Process -Id $process.ProcessId -Force
}

Write-Host "Stopped $($processes.Count) overlay process(es)."
