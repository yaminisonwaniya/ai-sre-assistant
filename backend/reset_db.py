"""Database reset and schema synchronization script."""
import os
import sys

# Add backend root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect
from app.db.database import Base, engine, SessionLocal
import app.models  # Register all models with Base.metadata


def reset_and_sync_database():
    """Drop and recreate all database tables to ensure 100% schema alignment."""
    print("Starting database schema reset and synchronization...")
    
    # Drop all existing tables
    Base.metadata.drop_all(bind=engine)
    print("Dropped old database tables.")

    # Recreate all tables based on Phase 3 models
    Base.metadata.create_all(bind=engine)
    print("Created fresh database tables aligned with all models.")

    # Verify using inspector
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Verified {len(tables)} database tables: {', '.join(tables)}")


if __name__ == "__main__":
    reset_and_sync_database()
