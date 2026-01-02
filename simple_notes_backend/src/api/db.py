import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_db_url() -> str:
    """
    Build a Postgres connection URL from environment variables.

    Tries:
    - POSTGRES_URL (if provided; can be full SQLAlchemy URL or DSN)
    - POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_PORT (host defaults to localhost)
    - Fallback to local dev default matching database/db_connection.txt

    Note: do not hardcode secrets; orchestrator should provide env vars in .env.
    """
    url = os.getenv("POSTGRES_URL")
    if url:
        # Allow either "postgresql://..." or "postgresql+psycopg://..."
        if url.startswith("postgresql://") or url.startswith("postgresql+psycopg://"):
            return url if "+psycopg" in url else url.replace("postgresql://", "postgresql+psycopg://", 1)
        # If some other DSN is provided, attempt to use it directly as SQLAlchemy URL.
        return url

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT")

    if user and password and db and port:
        return f"postgresql+psycopg://{user}:{password}@localhost:{port}/{db}"

    # Fallback for this template environment (from db_connection.txt)
    return "postgresql+psycopg://appuser:dbuser123@localhost:5000/myapp"


DB_URL = _build_db_url()

# Pool pre-ping helps avoid stale connections in containerized environments.
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy Session."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()
