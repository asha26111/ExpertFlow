#!/bin/bash
# DeepSeek EDU — One-click setup script
set -e

echo "═══════════════════════════════════════════════"
echo "  DeepSeek EDU Setup"
echo "═══════════════════════════════════════════════"

# ── Check Python ──────────────────────────────────
echo ""
echo "► Checking Python..."
if ! command -v python3 &>/dev/null; then
  echo "  ❌ Python 3 not found. Install from https://python.org"
  exit 1
fi
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  ✅ Python $PYVER found"

# ── Check PostgreSQL ──────────────────────────────
echo ""
echo "► Checking PostgreSQL..."
if ! command -v psql &>/dev/null; then
  echo "  ⚠️  psql not found. Install PostgreSQL first:"
  echo "     Ubuntu/Debian: sudo apt install postgresql"
  echo "     Mac:           brew install postgresql"
  echo "     Windows:       https://www.postgresql.org/download/"
else
  echo "  ✅ PostgreSQL found"
  echo "  Creating database 'deepseek_edu' if it doesn't exist..."
  createdb deepseek_edu 2>/dev/null && echo "  ✅ Database created" || echo "  ℹ️  Database already exists"
fi

# ── Backend setup ─────────────────────────────────
echo ""
echo "► Setting up backend..."
cd backend

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  ✅ .env created from .env.example"
  echo "  ⚠️  Edit backend/.env to set your DATABASE_URL and DEEPSEEK_API_KEY"
else
  echo "  ✅ .env exists"
fi

if [ ! -d "venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv venv
fi
echo "  ✅ Virtual environment ready"

echo "  Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
pip install -r requirements.txt -q
echo "  ✅ Python packages installed"
cd ..

# ── Frontend setup ────────────────────────────────
echo ""
echo "► Setting up frontend..."
cd frontend
if ! command -v node &>/dev/null; then
  echo "  ❌ Node.js not found. Install from https://nodejs.org"
  exit 1
fi
echo "  Installing npm packages..."
npm install --silent
echo "  ✅ npm packages installed"
cd ..

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Setup complete!"
echo "═══════════════════════════════════════════════"
echo ""
echo "  Before starting, edit backend/.env:"
echo "  • Set DATABASE_URL to match your PostgreSQL credentials"
echo "  • Set DEEPSEEK_API_KEY with your key from platform.deepseek.com"
echo ""
echo "  Then run in TWO terminals:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    python run.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Open: http://localhost:5173"
echo ""
