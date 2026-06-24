import os
import sys

# ── Force SQLite if DATABASE_URL still points to an unreachable PostgreSQL ────
db_url = os.environ.get("DATABASE_URL", "sqlite:///./data/deepseek_edu.db")
if "postgresql" in db_url or "postgres" in db_url:
    try:
        import sqlalchemy
        e = sqlalchemy.create_engine(db_url, connect_args={"connect_timeout": 3})
        with e.connect() as c:
            c.execute(sqlalchemy.text("SELECT 1"))
        print("✅ PostgreSQL OK")
    except Exception:
        print("⚠️  PostgreSQL unreachable — switching to SQLite")
        os.environ["DATABASE_URL"] = "sqlite:///./data/deepseek_edu.db"

import uvicorn

if __name__ == "__main__":
    print("")
    print("╔══════════════════════════════════════════╗")
    print("║           ExpertFlow Backend             ║")
    print("║     Gemini API • RAG • MoE Experts       ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Set GEMINI_API_KEY in .env to start     ║")
    print("║  Docs: /docs  Health: /health            ║")
    print("╚══════════════════════════════════════════╝")
    print("")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
