# ExpertFlow — AI-Powered Learning & Knowledge Platform
### Powered by Claude API • RAG • Mixture of Experts

Answers any question across 20+ domains — academics, skincare, coding, finance, career, lifestyle, and more.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, TailwindCSS, Zustand |
| **Backend** | FastAPI, Python 3.11+ |
| **LLM** | Claude API (claude-sonnet-4-6) |
| **Embeddings** | SentenceTransformers (all-MiniLM-L6-v2) |
| **Vector DB** | ChromaDB (persistent) |
| **SQL DB** | SQLite (default) or PostgreSQL |

---

## 🚀 Setup (2 steps)

### Step 1 — Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                   # → http://localhost:8000
```

### Step 2 — Frontend
```bash
cd frontend
npm install
npm run dev                     # → http://localhost:5173
```

---

## ⚙️ Configuration (`backend/.env`)

```env
# Database — SQLite by default, zero setup
DATABASE_URL=sqlite:///./data/expertflow.db

# Claude API (required) — get free key at https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-key-here

# JWT
SECRET_KEY=change-this-in-production

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
```

> **Get your free Claude API key at:** https://console.anthropic.com

---

## 🧠 Architecture

### RAG Pipeline
1. Query → SentenceTransformers embeds it
2. ChromaDB finds top-K relevant knowledge chunks
3. Retrieved context + expert system prompt sent to Claude API
4. Claude responds as the correct domain expert

### Mixture of Experts (20+ domains)
| Expert | Domain |
|--------|--------|
| 📐 Math Expert | Algebra, Calculus, Statistics |
| ⚛️ Physics Expert | Mechanics, Quantum, EM |
| 💻 CS Expert | Algorithms, ML, Coding, Sentence Transformers |
| 🧪 Chemistry Expert | Organic, Inorganic, Physical |
| 🧬 Biology Expert | Genetics, Cell biology, Anatomy |
| 📜 History Expert | World history, Civilizations |
| 🌍 Geography Expert | Physical + Human geography |
| 📊 Economics Expert | Micro, Macro, Finance |
| 📚 Literature Expert | Analysis, Grammar, Writing |
| 🧠 Psychology Expert | Cognitive, Social, Clinical |
| 🤔 Philosophy Expert | Ethics, Logic, Epistemology |
| ∑ Advanced Math | Analysis, Algebra, Topology |
| 🏥 Health & Lifestyle | Skincare, Haircare, Diet, Fitness, Wellness |
| 💰 Finance Expert | Investing, Budgeting, Crypto, Tax |
| 💼 Career Expert | Resume, Interviews, Career growth |
| 🎬 Entertainment | Movies, Music, TV, Gaming |
| 📱 Technology | Gadgets, AI tools, Software |
| 🔬 Science Expert | Space, Climate, Discoveries |
| 📰 Current Affairs | News, Politics, World events |
| 🌐 General Knowledge | Cooking, Travel, Lifestyle, Everything else |
| 💬 Chat Companion | Casual chat, Jokes, Recommendations |

---

## 🌐 Deploying to Render

1. Push this repo to GitHub
2. Go to https://render.com → **New → Blueprint**
3. Connect your GitHub repo (Render auto-detects `render.yaml`)
4. Add environment variable: `ANTHROPIC_API_KEY=sk-ant-your-key`
5. Click **Apply** — live in ~5 minutes

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| GET | `/api/chats` | List chats |
| POST | `/api/chats` | New chat |
| POST | `/api/chats/{id}/messages` | Send message → RAG + MoE + Claude |
| GET | `/api/subjects` | List all subjects |
