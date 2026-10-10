"""Database setup module for SQLAlchemy ORM sessions and engines."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase
from app.config import settings

# Engine configuration - supports SQLite and PostgreSQL transparently
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


def get_db():
    """Dependency provider for FastAPI endpoint database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
