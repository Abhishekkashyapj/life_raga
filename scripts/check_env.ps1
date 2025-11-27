Write-Host "Checking environment..."

# Check python
python --version 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "Python not found" -ForegroundColor Red }
else { Write-Host "Python OK" -ForegroundColor Green }

# Check Docker
docker info 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "Docker not accessible" -ForegroundColor Yellow }
else { Write-Host "Docker OK" -ForegroundColor Green }

# Check Ollama
ollama --version 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "Ollama not installed or not on PATH" -ForegroundColor Yellow }
else { Write-Host "Ollama present" -ForegroundColor Green }

Write-Host "Done"
