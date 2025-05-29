"""Middleware for API request handling."""
from typing import Callable
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.database import SessionLocal
from app.models.monitoring import AuditLog
import json

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging of API requests."""

    def __init__(
        self,
        app: ASGIApp,
        audit_paths: list[str] = None
    ):
        super().__init__(app)
        self.audit_paths = audit_paths or [
            "/users",
            "/academic",
            "/records",
            "/grades",
            "/attendance"
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request and log if necessary."""
        # Generate request ID if not already set
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid4())

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = str(request.state.request_id)

        # Check if path should be audited
        if any(path in request.url.path for path in self.audit_paths):
            # Get user from request state if available
            user = getattr(request.state, "user", None)
            
            # Create DB session
            db = SessionLocal()
            try:
                # Create audit log entry for sensitive endpoints
                entity_type = request.url.path.split("/")[-1]
                entity_id = "unknown"
                
                # Try to extract entity ID from path
                path_parts = request.url.path.split("/")
                if len(path_parts) > 1:
                    possible_id = path_parts[-1]
                    if possible_id not in ["", entity_type]:
                        entity_id = possible_id

                # Extract request body for POST/PUT operations
                changes = None
                if request.method in ["POST", "PUT"] and request.headers.get("content-type") == "application/json":
                    try:
                        body = await request.json()
                        # Filter out sensitive data
                        if isinstance(body, dict):
                            changes = {k: v for k, v in body.items() if k not in ["password", "password_hash"]}
                    except:
                        changes = None

                # Create audit log entry
                audit_log = AuditLog(
                    user_id=user.id if user else None,
                    action=request.method.lower(),
                    entity_type=entity_type,
                    entity_id=entity_id,
                    changes=changes,
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                    details=f"Request to {request.url.path} [Method: {request.method}]"
                )
                db.add(audit_log)
                db.commit()
            except Exception as e:
                # Log error but don't stop request processing
                print(f"Error in audit logging: {str(e)}")
            finally:
                db.close()

        return response
