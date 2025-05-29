"""Endpoints package for v1 API."""
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.academic import router as academic_router
from app.api.v1.endpoints.records import router as records_router
from app.api.v1.endpoints.content import router as content_router
from app.api.v1.endpoints.registration import router as registration_router
from app.api.v1.endpoints.monitoring import router as monitoring_router

__all__ = [
    "auth_router",
    "users_router",
    "academic_router",
    "records_router",
    "content_router",
    "registration_router",
    "monitoring_router",
]
