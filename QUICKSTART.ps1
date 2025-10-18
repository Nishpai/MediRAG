# MediRAG - Quick Start Guide

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║             🏥  MediRAG - Medical FAQ Bot  🏥                ║
║          AI-Powered Health Assistant with RAG                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 Quick Start Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "STEP 1: Add your OpenAI API key:" -ForegroundColor White
Write-Host "   Edit: backend\.env" -ForegroundColor Gray
Write-Host "   Replace 'your-openai-api-key-here' with your actual key" -ForegroundColor Gray
Write-Host "   Get a key at: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host ""
Write-Host "STEP 2: Start the Backend (Flask + RAG Pipeline):" -ForegroundColor White
Write-Host "   .\start-backend.ps1" -ForegroundColor Green
Write-Host "   Runs on http://localhost:5000" -ForegroundColor Gray
Write-Host "   First run builds vector store (takes 20 seconds)" -ForegroundColor Gray
Write-Host ""
Write-Host "STEP 3: Start the Frontend (React + Tailwind) - IN A NEW TERMINAL:" -ForegroundColor White
Write-Host "   .\start-frontend.ps1" -ForegroundColor Green
Write-Host "   Opens automatically at http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "STEP 4: Test the API (Optional):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python test_query.py" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Example Questions to Ask the Bot:" -ForegroundColor Yellow
Write-Host "   What are the symptoms of diabetes?" -ForegroundColor Gray
Write-Host "   How can I prevent heart disease?" -ForegroundColor Gray
Write-Host "   What is a healthy BMI range?" -ForegroundColor Gray
Write-Host "   What foods help lower cholesterol?" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "   Keep both terminals open while using the app" -ForegroundColor Gray
Write-Host "   Backend must be running before starting frontend" -ForegroundColor Gray
Write-Host "   Check README.md for full documentation" -ForegroundColor Gray
Write-Host ""
Write-Host "Need Help? Check:" -ForegroundColor Yellow
Write-Host "   README.md - Full setup guide" -ForegroundColor Gray
Write-Host "   backend/test_query.py - API testing" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
