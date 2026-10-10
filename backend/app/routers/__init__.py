"""Routers package init."""
from app.routers.health import router as health_router
from app.routers.projects import router as projects_router
from app.routers.requirements import router as requirements_router

__all__ = ["health_router", "projects_router", "requirements_router"]
