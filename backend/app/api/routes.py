from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Basic liveness check.
    Returns 200 OK when the service is running.
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }