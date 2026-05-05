from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import router as api_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time face detection over WebSocket streams.",
)

app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Face Detection API is running. Visit /health for status."
    }