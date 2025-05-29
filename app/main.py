"""Main FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.middleware import AuditMiddleware

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        College Portal API provides a comprehensive interface for managing college operations.
        
        ## Features
        
        * User Management (students, staff, administrators)
        * Academic Records (enrollments, grades, attendance)
        * Content Management (news, events)
        * Event Registration
        * Monitoring and Reporting
        * Audit Logging
        
        ## Authentication
        
        This API uses JWT tokens for authentication. To access protected endpoints:
        
        1. Obtain a token using the `/api/v1/auth/login` endpoint
        2. Include the token in the Authorization header: `Bearer <token>`
        
        ## Authorization
        
        The API implements role-based access control with the following roles:
        
        * ADMIN: Full system access
        * STAFF: Academic and student management
        * STUDENT: Limited access to own records
        """,
        routes=app.routes,
    )
    
    # Security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter the JWT token obtained from the login endpoint"
        }
    }
    
    # Global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Add response examples
    openapi_schema["components"]["examples"] = {
        "UserResponse": {
            "summary": "Example user response",
            "value": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
                "is_active": True,
                "is_superuser": False
            }
        },
        "ErrorResponse": {
            "summary": "Example error response",
            "value": {
                "detail": "Not authorized to perform this action"
            }
        }
    }
    
    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Operations for authentication and token management"
        },
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "academic",
            "description": "Student and staff academic management"
        },
        {
            "name": "records",
            "description": "Academic records including grades and attendance"
        },
        {
            "name": "content",
            "description": "News and events management"
        },
        {
            "name": "registration",
            "description": "Event registration and reporting"
        },
        {
            "name": "monitoring",
            "description": "System monitoring and audit logging"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the College Portal API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json"
    }
