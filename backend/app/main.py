import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import router as api_router
from app.api.ws import router as ws_router
from app.api.roi import router as roi_router
from app.db.database import create_tables

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    logger.info("DB tables created successfully")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(api_router)
app.include_router(ws_router)
app.include_router(roi_router)

@app.get("/")
async def root():
    return {"message": "Face Detection API is running. Visit /health for status."}