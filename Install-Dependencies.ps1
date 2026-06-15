$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

function Resolve-Python {
    $candidates = @(
        @{ Command = 'py'; Args = @('-3.12') },
        @{ Command = 'python'; Args = @() }
    )

    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if (-not $command) {
            continue
        }

        $probe = & $candidate.Command @($candidate.Args) -c "import sys; print(sys.executable); print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -eq 0 -and $probe.Count -ge 2) {
            if ([version]$probe[1] -eq [version]'3.12') {
                return @{ Command = $candidate.Command; Args = $candidate.Args; Version = $probe[1] }
            }
        }
    }

    throw 'Python 3.12 is required for building the packaged app.'
}

$python = Resolve-Python
Write-Host "Using Python $($python.Version)"
& $python.Command @($python.Args) -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to upgrade pip.'
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to install dependencies.'
}

Write-Host 'Dependencies installed.'
Write-Host 'Run Run-Overlay.bat to start the app.'
