# 🏥 MediRAG - Setup Complete!

## ✅ What's Been Installed

### Backend (Python/Flask)
- ✅ Virtual environment created
- ✅ All Python dependencies installed (Flask, LangChain, FAISS, OpenAI)
- ✅ Environment file created (.env)

### Frontend (React/Vite)
- ✅ Node modules installed
- ✅ React, Tailwind CSS, Axios configured
- ✅ Environment file created (.env)

---

## 🚀 NEXT STEPS TO RUN THE APP

### ⚠️ STEP 1: Add Your OpenAI API Key (REQUIRED!)

1. Open the file: `backend\.env`
2. Replace `your-openai-api-key-here` with your actual OpenAI API key
3. Get an API key at: https://platform.openai.com/api-keys

Example:
```
OPENAI_API_KEY=sk-proj-abc123xyz...
```

---

### 🔧 STEP 2: Start the Backend Server

Open a PowerShell terminal in this directory and run:

```powershell
.\start-backend.ps1
```

**What happens:**
- ✅ Activates Python virtual environment
- ✅ Loads medical FAQ data (25+ topics)
- ✅ Builds FAISS vector store (first run only, takes ~20 seconds)
- ✅ Starts Flask server on http://localhost:5000

**Keep this terminal open!**

---

### 🎨 STEP 3: Start the Frontend Server

Open a **NEW** PowerShell terminal in this directory and run:

```powershell
.\start-frontend.ps1
```

**What happens:**
- ✅ Starts Vite development server
- ✅ Opens browser automatically at http://localhost:3000
- ✅ Hot reload enabled for development

**Keep this terminal open too!**

---

## 🧪 STEP 4: Test the Application

### Option A: Use the Web Interface
1. Browser should open automatically at http://localhost:3000
2. Type a medical question like:
   - "What are the symptoms of diabetes?"
   - "How can I prevent heart disease?"
   - "What is a healthy BMI range?"
3. See the AI-powered response with sources!

### Option B: Test the API Directly
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python test_query.py
```

This runs comprehensive tests on the backend API.

---

## 📁 Project Structure

```
MediRAG/
├── backend/
│   ├── main.py              ← Flask API server
│   ├── rag_pipeline.py      ← RAG logic (embeddings, retrieval)
│   ├── data/
│   │   └── medical_faqs.txt ← Knowledge base (25+ Q&A)
│   ├── vectorstore/         ← FAISS index (auto-generated)
│   ├── .env                 ← YOUR API KEY GOES HERE!
│   └── venv/                ← Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          ← Main React component
│   │   ├── components/      ← Chat UI components
│   │   └── api.js           ← Backend API client
│   └── node_modules/        ← React dependencies
│
├── start-backend.ps1        ← Quick start backend
├── start-frontend.ps1       ← Quick start frontend
├── QUICKSTART.ps1           ← Show instructions
└── README.md                ← Full documentation
```

---

## 🎯 Example Questions to Ask

```
✅ What are the symptoms of diabetes?
✅ How can I prevent heart disease?
✅ What is hypertension and how is it managed?
✅ How much sleep do adults need?
✅ What is a healthy BMI range?
✅ What foods help lower cholesterol?
✅ What are the warning signs of a stroke?
✅ How can I boost my immune system naturally?
✅ What is the DASH diet?
✅ What causes migraine headaches?
```

---

## 🛠️ Troubleshooting

### "OPENAI_API_KEY not found"
- ✅ Make sure you edited `backend\.env`
- ✅ Replace the placeholder with your actual API key
- ✅ No quotes needed around the key

### "Unable to connect to server"
- ✅ Make sure backend is running first (Step 2)
- ✅ Check that port 5000 is not in use
- ✅ Look for errors in the backend terminal

### "Port already in use"
- ✅ Close any previous instances
- ✅ Change ports in the config files if needed

### Backend won't start
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
python main.py
```

### Frontend won't start
```powershell
cd frontend
Remove-Item node_modules -Recurse -Force
npm install
npm run dev
```

---

## 📊 Performance Expectations

| Metric | Expected Value |
|--------|----------------|
| First query (uncached) | 1.5 - 3.0 seconds |
| Cached query | 0.1 - 0.3 seconds |
| Vector store build | 10 - 20 seconds (one-time) |
| Page load time | < 1 second |

---

## 🔒 Security Notes

- ⚠️ Never commit your `.env` file to Git
- ⚠️ Keep your OpenAI API key private
- ⚠️ The app is for development/demo only (not production-ready)
- ⚠️ Set up proper authentication for production use

---

## 📚 Additional Resources

- **Full README:** `README.md` (comprehensive guide)
- **API Testing:** `backend/test_query.py`
- **Medical Data:** `backend/data/medical_faqs.txt`
- **OpenAI Docs:** https://platform.openai.com/docs
- **LangChain Docs:** https://python.langchain.com/docs

---

## 💡 Tips

1. **Keep both terminals open** while using the app
2. **Backend must start first** before the frontend
3. **First run is slower** (builds vector store)
4. **Cached queries are faster** (~0.2s vs 2s)
5. **Check the Sources button** in responses for transparency
6. **Use the Clear Chat button** to reset conversation

---

## 🎉 You're All Set!

Your Medical FAQ Bot is ready to use! Just:
1. ✅ Add your OpenAI API key to `backend\.env`
2. ✅ Run `.\start-backend.ps1`
3. ✅ Run `.\start-frontend.ps1` (in new terminal)
4. ✅ Start asking medical questions!

---

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the full README.md
3. Make sure your OpenAI API key is valid and has credits
4. Ensure Python 3.10+ and Node.js 18+ are installed

**Enjoy your AI Medical Assistant! 🏥**
