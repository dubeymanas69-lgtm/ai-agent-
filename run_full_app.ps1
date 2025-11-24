$env:LLM_API_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
$env:LLM_API_KEY="AIzaSyCj84RA3FGvGeb4PL58VQirKP7tTxGlENQ"

# Kill any process listening on port 8000 (cleanup old server)
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    Write-Host "Killing old server on port 8000..."
    Stop-Process -Id $portProcess.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Start Server
Write-Host "Starting AI Task Manager..."
Start-Process -FilePath "python" -ArgumentList "project/server.py"

# Wait a moment for server to start
Start-Sleep -Seconds 2

# Open Browser
Start-Process "http://localhost:8000"
