# ExpertFlow — Deployment Guide

## Backend → Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Docker
   - **Dockerfile Path:** `./Dockerfile`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = your AQ. key from aistudio.google.com
   - `SECRET_KEY` = any random 32+ char string
6. Click **Deploy**
7. Copy your Render URL → e.g. `https://expertflow-backend.onrender.com`

> Render's free tier spins down after inactivity — first request after idle takes ~30s.

---

## Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import the same GitHub repo
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework:** Vite
4. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://your-render-url.onrender.com/api`
5. Click **Deploy**

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # then add your GEMINI_API_KEY
python run.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```
