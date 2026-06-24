from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

app = FastAPI(
    title="ExpertFlow",
    description="AI Learning Platform — Gemini 2.5 Flash + RAG + MoE",
    version="1.0.0",
)

# ── CORS: open for development ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import auth, chats, subjects  # noqa

app.include_router(auth.router, prefix="/api")
app.include_router(chats.router, prefix="/api")
app.include_router(subjects.router, prefix="/api")


# ── Global error handler — always returns JSON, never crashes ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    try:
        from app.core.database import create_tables
        create_tables()
    except Exception as e:
        print(f"❌ DB startup error: {e}")

    # Pre-load RAG service in background so first query isn't slow
    import asyncio
    import threading

    def _preload():
        try:
            from app.services.rag_service import get_rag_service
            get_rag_service()
            print("✅ RAG service pre-loaded")
        except Exception as e:
            print(f"⚠️  RAG pre-load warning: {e}")

    t = threading.Thread(target=_preload, daemon=True)
    t.start()


# ── Health checks ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "ExpertFlow API running", "version": "1.0.0"}


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "healthy"}
