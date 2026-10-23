from fastapi import FastAPI

app = FastAPI(
    title="LeadForge API",
    description="Evidence-first sales intelligence for SaaS prospect research.",
    version="0.1.0",
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint returning service operational status."""
    return {"status": "ok"}
