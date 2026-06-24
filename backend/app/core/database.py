import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def _build_engine():
    # Import here to allow config.py to have already patched DATABASE_URL
    from app.core.config import settings
    url = settings.DATABASE_URL

    if url.startswith("sqlite"):
        os.makedirs("./data", exist_ok=True)
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            # pool_size for SQLite must stay at 1 to avoid thread issues
            poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
        )

    # PostgreSQL
    return create_engine(url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    from app.models import user, chat, subject  # noqa
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
