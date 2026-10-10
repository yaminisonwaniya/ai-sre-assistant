"""Health check API router for uptime and comprehensive database schema verification."""
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.db.database import Base, get_db
import app.models  # Register all models with Base.metadata
from app.config import settings

router = APIRouter(tags=["Health"])


def verify_database_schema(db: Session):
    """Verify that all expected ORM tables and columns exist in the database."""
    engine = db.get_bind()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    missing_tables = []
    missing_columns = []

    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            missing_tables.append(table_name)
        else:
            existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
            expected_cols = {col.name for col in table.columns}
            missing_in_table = expected_cols - existing_cols
            if missing_in_table:
                missing_columns.append(f"{table_name}(missing: {', '.join(sorted(missing_in_table))})")

    if missing_tables or missing_columns:
        err_msg = []
        if missing_tables:
            err_msg.append(f"Missing tables: {', '.join(missing_tables)}")
        if missing_columns:
            err_msg.append(f"Missing columns: {'; '.join(missing_columns)}")
        return False, "schema_mismatch: " + " | ".join(err_msg)

    return True, "healthy"


@router.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)):
    """Health check verifying API uptime and full database schema integrity (tables & columns)."""
    is_healthy, db_status = verify_database_schema(db)

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "database": db_status,
            "llm_provider": settings.LLM_PROVIDER,
        }

    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_status,
        "llm_provider": settings.LLM_PROVIDER,
    }
