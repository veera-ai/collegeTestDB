"""Main router for v1 API."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    academic,
    records,
    content,
    registration,
    monitoring
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(registration.router, prefix="/registration", tags=["registration"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
