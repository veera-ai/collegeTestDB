"""Middleware for API request handling."""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

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
        response = await call_next(request)
        
        # Add audit-related headers
        response.headers["X-Request-ID"] = str(request.state.request_id)
        
        return response
