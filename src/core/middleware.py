# Cross-cutting ASGI middleware: request IDs and security headers
import uuid

import structlog
from starlette.datastructures import Headers
from starlette.datastructures import MutableHeaders

from src.core.config import src_setting


class RequestIDMiddleware:
    """Propagate an incoming X-Request-ID (or generate one) and bind it to the request's logs."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = Headers(scope=scope).get("x-request-id") or uuid.uuid4().hex

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_with_request_id(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_with_request_id)


class SecurityHeadersMiddleware:
    """Add a conservative set of security headers to every response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if "x-content-type-options" not in headers:
                    headers["X-Content-Type-Options"] = "nosniff"
                if "x-frame-options" not in headers:
                    headers["X-Frame-Options"] = "DENY"
                if "referrer-policy" not in headers:
                    headers["Referrer-Policy"] = "no-referrer"
                # HSTS only makes sense when TLS is in front (i.e. production)
                if src_setting.ENVIRONMENT == "production" and "strict-transport-security" not in headers:
                    headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            await send(message)

        await self.app(scope, receive, send_with_headers)


def get_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS (comma-separated) into a list of allowed origins."""
    return [origin.strip() for origin in src_setting.CORS_ORIGINS.split(",") if origin.strip()]
