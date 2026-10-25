"""FastAPI application entry point for LeadForge API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_export, routes_icp, routes_prospects
from app.core.config import settings
from app.db.seed_data import seed_initial_data
from app.db.session import check_db_health, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle.

    Ensures SQLite tables, indexes, and initial demo seed data are ready on boot.
    """
    await init_db()
    await seed_initial_data()
    yield


app = FastAPI(
    title="LeadForge API",
    description="Evidence-first sales intelligence for SaaS prospect research.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS explicitly for documented local frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api prefix
app.include_router(routes_icp.router, prefix="/api")
app.include_router(routes_prospects.router, prefix="/api")
app.include_router(routes_export.router, prefix="/api")


@app.get("/api/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint returning service operational status and DB connectivity."""
    db_healthy = await check_db_health()
    status_str = "ok" if db_healthy else "degraded"
    return {"status": status_str, "db": db_healthy}
