# MediRAG - Start Frontend Server
# This script starts the Vite development server

Write-Host "🎨 Starting MediRAG Frontend Server..." -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location -Path $PSScriptRoot\frontend

# Start Vite dev server
Write-Host "🚀 Starting Vite dev server on http://localhost:3000" -ForegroundColor Green
Write-Host "   The browser will open automatically" -ForegroundColor Gray
Write-Host ""
npm run dev
