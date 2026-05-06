from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import get_settings
from app.services.face_detection import detect_face
from PIL import Image
import io

router = APIRouter()
settings = get_settings()


@router.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }


@router.post("/test-detect", tags=["test"])
async def test_detect(file: UploadFile = File(...)):
    """
    Temporary test endpoint.
    Upload an image → get back face ROI coordinates.
    Remove this once WebSocket streaming is working.
    """
    # validate it's an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()

    try:
        pil_image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image")

    roi = detect_face(pil_image)

    if roi is None:
        return {"face_detected": False, "roi": None}

    return {"face_detected": True, "roi": roi}