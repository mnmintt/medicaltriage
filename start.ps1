# TriageAI - Start Script for Windows

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "      TriageAI - Groq Swarm Edition          " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Check for API key
$EnvPath = Join-Path -Path $PSScriptRoot -ChildPath "backend\.env"

# Ensure Node.js is in the PATH for this session (needed for Vite)
if (Test-Path "C:\Program Files\nodejs\node.exe") {
    $env:PATH = "C:\Program Files\nodejs;" + $env:PATH
}

if (-not (Test-Path $EnvPath)) {
    Write-Host "[ERROR] backend\.env not found. Please create it with GROQ_API_KEY=gsk_..." -ForegroundColor Red
    exit 1
}
else {
    Write-Host "[OK] backend\.env detected." -ForegroundColor Green
}

# Find Python 3.11 explicitly since it might not be default
$PythonCmd = "python"
if (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe") {
    $PythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
}

# 2. Install backend dependencies
Write-Host "`n[BACKEND] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location -Path (Join-Path -Path $PSScriptRoot -ChildPath "backend")
& $PythonCmd -m pip install -r requirements.txt -q
Set-Location -Path $PSScriptRoot

# 3. Install frontend dependencies
Write-Host "[FRONTEND] Installing Node dependencies..." -ForegroundColor Yellow
Set-Location -Path (Join-Path -Path $PSScriptRoot -ChildPath "frontend")

# Try to use npm, or fallback to the full path if recently installed
$NpmCmd = "npm"
if (-not (Get-Command npm -ErrorAction SilentlyContinue) -and (Test-Path "C:\Program Files\nodejs\npm.cmd")) {
    $NpmCmd = "C:\Program Files\nodejs\npm.cmd"
}
& $NpmCmd install --silent
Set-Location -Path $PSScriptRoot

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "[STARTING] Flask backend on http://localhost:8080" -ForegroundColor Cyan
Write-Host "[STARTING] Vite frontend on http://localhost:5173" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 4. Start backend in background (new window)
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; `$env:FLASK_ENV='development'; & '$PythonCmd' server.py`""

Start-Sleep -Seconds 2

# 5. Start frontend in background (new window)
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; & '$NpmCmd' run dev`""

Write-Host "`n✅ Both services started in separate windows!" -ForegroundColor Green
Write-Host "   Frontend: http://localhost:5173"
Write-Host "   Backend:  http://localhost:8080"
Write-Host "   Health:   http://localhost:8080/api/health"
Write-Host "   Demo:     http://localhost:8080/api/demo"
Write-Host "`nClose the two popped-up PowerShell windows to stop the services."
