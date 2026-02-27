# 🎯 AI Interview Preparation Coach

An AI-powered interview simulator built with Streamlit, Google Gemini, and Groq.

## ✨ Features
- **HR, Behavioral & Technical** interview modes
- **Live code editor** with support for Python, C, C++, Java, C#, JavaScript
- **Real-time AI feedback** with scores, strengths, and improvements
- **Skill Gap Analysis** with a personalised improvement plan
- **Dual LLM fallback** — Groq (fast) + Gemini (deep analysis)

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add API keys
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-gemini-key"
GROQ_API_KEY   = "your-groq-key"
```
Get keys from:
- Gemini: https://aistudio.google.com/app/apikey
- Groq:   https://console.groq.com/keys

### 3. Run the app
```bash
streamlit run app.py
```

## 🔒 Security
- Never commit `secrets.toml` to Git — it's in `.gitignore`
- For Streamlit Cloud deployment, use the dashboard's Secrets manager
