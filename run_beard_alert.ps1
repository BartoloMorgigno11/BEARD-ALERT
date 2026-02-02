$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPath = Join-Path $root ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[1/3] Creating virtual environment..."
    python -m venv $venvPath
}

Write-Host "[2/3] Installing dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $root "requirements.txt")

Write-Host "[3/3] Starting Beard Alert..."
& $pythonExe (Join-Path $root "src\main.py")
