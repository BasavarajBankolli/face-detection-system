import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

from app.core.config import get_settings
from app.services.face_detection import detect_face
from app.services.image_utils import draw_bounding_box, image_to_base64

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
    Upload image → detect face → draw ROI → return image + coordinates.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()

    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image")

    # step 1 — detect face
    roi = detect_face(pil_image)

    if roi is None:
        return {
            "face_detected": False,
            "roi": None,
            "image": image_to_base64(pil_image)  # return original image
        }

    # step 2 — draw bounding box
    annotated_image = draw_bounding_box(pil_image, roi)

    # step 3 — convert to base64 for frontend
    image_b64 = image_to_base64(annotated_image)

    return {
        "face_detected": True,
        "roi": roi,
        "image": image_b64
    }
