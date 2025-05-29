"""Main FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.middleware import AuditMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add audit middleware
app.add_middleware(
    AuditMiddleware,
    audit_paths=[
        f"{settings.API_V1_STR}/users",
        f"{settings.API_V1_STR}/auth",
        f"{settings.API_V1_STR}/academic",
        f"{settings.API_V1_STR}/records",
        f"{settings.API_V1_STR}/grades",
        f"{settings.API_V1_STR}/attendance",
        f"{settings.API_V1_STR}/content",
        f"{settings.API_V1_STR}/registration",
        f"{settings.API_V1_STR}/monitoring",
    ]
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the College Portal API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
