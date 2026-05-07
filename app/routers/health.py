from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import text

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return {
        "status": "ok",
        "db_ok": db_ok,
        "model_loaded": False,
        "model_version": None
    }
