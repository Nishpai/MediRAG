# MediRAG - Start Backend Server
# This script activates the virtual environment and starts the Flask server

Write-Host "🏥 Starting MediRAG Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location -Path $PSScriptRoot\backend

# Check if .env file exists and has API key
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your-openai-api-key-here|your-gemini-api-key-here") {
        Write-Host "⚠️  WARNING: Please add your Google Gemini API key to backend\.env" -ForegroundColor Yellow
        Write-Host "   Edit the file and replace the placeholder with your actual Gemini API key" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to continue anyway or Ctrl+C to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} else {
    Write-Host "❌ Error: .env file not found in backend directory" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Start Flask server
Write-Host ""
Write-Host "🚀 Starting Flask server on http://localhost:5000" -ForegroundColor Green
Write-Host ""
python main.py
