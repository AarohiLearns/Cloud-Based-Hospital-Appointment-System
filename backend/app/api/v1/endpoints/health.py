from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness() -> dict:
    """Used by the ALB / ECS health check."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(db: DbSession) -> dict:
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
