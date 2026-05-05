from fastapi import FastAPI
from app.health import router as health_router

app = FastAPI()

app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Face Detection API is running. Visit /health for status."}
