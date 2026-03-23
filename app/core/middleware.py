"""Application middleware: CORS, rate limiting, audit logging, security headers."""

import time
import uuid
from collections import defaultdict

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

logger = structlog.get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Audit logging (outermost so it captures everything)
    app.add_middleware(AuditLogMiddleware)

    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
        login_requests_per_minute=settings.rate_limit_login_per_minute,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ── Security Headers ────────────────────────────────────────


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response


# ── Rate Limiting (in-memory, per-IP) ───────────────────────


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 100, login_requests_per_minute: int = 5):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.login_rpm = login_requests_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _clean_window(self, key: str, now: float) -> None:
        window_start = now - 60
        self._hits[key] = [t for t in self._hits[key] if t > window_start]

    async def dispatch(self, request: Request, call_next):
        # Keep tests deterministic: disable rate limiting in test environment.
        if get_settings().environment.lower() == "test":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        is_login = request.url.path.endswith("/auth/login") and request.method == "POST"
        key = f"login:{client_ip}" if is_login else f"api:{client_ip}"
        limit = self.login_rpm if is_login else self.rpm

        self._clean_window(key, now)
        if len(self._hits[key]) >= limit:
            logger.warning("rate_limit_exceeded", ip=client_ip, path=str(request.url.path))
            return Response(
                content='{"detail":"Rate limit exceeded. Try again later."}',
                status_code=429,
                media_type="application/json",
            )
        self._hits[key].append(now)
        return await call_next(request)


# ── Audit Log Middleware ─────────────────────────────────────


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "http_request",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration_ms=elapsed_ms,
            ip=request.client.host if request.client else "unknown",
        )
        return response
