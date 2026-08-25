# ============================================================
# VeristasOS — One-Terminal Windows Launcher
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "       VERISTASOS — TRUTH INTELLIGENCE PLATFORM            " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Environment & Path Resolution
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[✓] Python Environment : Found venv ($venvPython)" -ForegroundColor Green
    $pythonCmd = $venvPython
} else {
    Write-Host "[!] Virtual environment not found at .\venv, using system python." -ForegroundColor Yellow
    $pythonCmd = "python"
}

# 2. Check Local llama.cpp AI Server Status
Write-Host "[*] Checking Local AI (llama.cpp) at http://127.0.0.1:8080 ..." -NoNewline
try {
    $aiCheck = Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host " CONNECTED" -ForegroundColor Green
    Write-Host "    Model: Qwen2.5 3B Instruct GGUF" -ForegroundColor Gray
} catch {
    Write-Host " OFFLINE" -ForegroundColor Yellow
    Write-Host "    Note: VeristasOS will operate in deterministic mode." -ForegroundColor Gray
    Write-Host "    To enable local Qwen AI, start llama-server on http://127.0.0.1:8080." -ForegroundColor Gray
}

# 3. Print Operating URLs
Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkGray
Write-Host " Frontend Interface : http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host " API Documentation  : http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host " Health Endpoint    : http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Starting VeristasOS FastAPI Server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to terminate the server." -ForegroundColor Gray
Write-Host ""

# 4. Launch FastAPI Uvicorn Server
& $pythonCmd -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
