"""FastAPI application entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, jobs
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

DESCRIPTION = """
REST API for tracking job applications.

**Authentication** — call `POST /auth/register` or `POST /auth/login` to receive a
JWT access token, then send it as `Authorization: Bearer <token>` on every
`/jobs` request. The interactive docs provide an **Authorize** button for this.

**Isolation** — job applications are strictly scoped to the authenticated user;
requests for another user's application return `404`.
"""

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

allowed_origins = settings.cors_origin_list
# A wildcard origin cannot be combined with credentialed requests per the CORS
# spec, so credentials are only allowed for explicitly listed origins.
wildcard_origin = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=not wildcard_origin,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=3600,
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["meta"], summary="API metadata")
def read_root() -> dict[str, str]:
    """Identify the service and point clients at the docs."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"], summary="Liveness probe")
def health_check() -> dict[str, str]:
    """Cheap endpoint for uptime checks; does not touch the database."""
    return {"status": "ok"}
