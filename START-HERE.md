# 🏥 MediRAG - Quick Reference Card

## ⚠️ BEFORE YOU START - ONE TIME SETUP REQUIRED!

### 🔑 Step 1: Add Your OpenAI API Key (REQUIRED!)

Open this file in Notepad:
```
backend\.env
```

Replace this line:
```
OPENAI_API_KEY=your-openai-api-key-here
```

With your actual key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Get a key at:** https://platform.openai.com/api-keys

Save and close the file.

---

## 🚀 TO RUN THE APP (After adding API key):

### Terminal 1 - Start Backend:
```powershell
cd C:\Users\nishp\OneDrive\Desktop\Projects\MediRAG
.\start-backend.ps1
```
**Wait for:** "Running on http://127.0.0.1:5000" message
**Keep this terminal open!**

### Terminal 2 - Start Frontend (NEW terminal):
```powershell
cd C:\Users\nishp\OneDrive\Desktop\Projects\MediRAG
.\start-frontend.ps1
```
**Browser opens at:** http://localhost:3000

---

## 📝 Project Location
```
C:\Users\nishp\OneDrive\Desktop\Projects\MediRAG
```

## 📚 Documentation Files
- **SETUP-COMPLETE.md** - Detailed setup guide
- **README.md** - Full documentation
- **backend/test_query.py** - API testing script

## 🎯 Example Questions to Ask the Bot
```
What are the symptoms of diabetes?
How can I prevent heart disease?
What is a healthy BMI range?
What foods help lower cholesterol?
What are the warning signs of a stroke?
```

## 🛠️ Project Status
✅ Backend dependencies installed (Flask, LangChain, FAISS, OpenAI)
✅ Frontend dependencies installed (React, Vite, Tailwind CSS)
✅ Medical FAQ database created (25+ topics)
✅ Environment files created
⚠️ NEEDS: Your OpenAI API key in backend\.env

## 📂 Key Files You Might Need
```
backend\.env              ← Add your API key here
backend\main.py           ← Flask server
backend\rag_pipeline.py   ← RAG implementation
backend\data\medical_faqs.txt  ← Medical knowledge base
frontend\src\App.jsx      ← React main component
```

## 🆘 Quick Troubleshooting
**"OPENAI_API_KEY not found"**
→ Edit backend\.env and add your key

**"Port already in use"**
→ Close previous instances or restart your computer

**Backend won't start**
→ Make sure you're in the project directory
→ Run: .\start-backend.ps1

**Frontend won't start**
→ Make sure backend is running first
→ Run: .\start-frontend.ps1

---

## ⚡ QUICK START COMMANDS

When you're ready to run (after adding API key):

**Option 1 - Use Helper Scripts:**
```powershell
# Terminal 1
.\start-backend.ps1

# Terminal 2 (NEW window)
.\start-frontend.ps1
```

**Option 2 - Manual Start:**
```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 💡 Remember
1. Add OpenAI API key to backend\.env first!
2. Start backend BEFORE frontend
3. Keep both terminals open while using the app
4. First run takes ~20 seconds (builds vector store)
5. Browser opens automatically at http://localhost:3000

---

**Created:** October 15, 2025
**Project:** MediRAG - AI Medical FAQ Bot with RAG Architecture
**Stack:** React + Flask + LangChain + OpenAI + FAISS

🎉 Everything is installed and ready to go!
Just add your OpenAI API key and run the start scripts!
