import io
import base64
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from PIL import Image

from app.services.face_detection import detect_face
from app.services.image_utils import draw_bounding_box, image_to_base64
from app.db.database import SessionLocal
from app.models.roi import ROIDetection

router = APIRouter()

SAVE_EVERY_N_FRAMES = 5  # save to DB every 5 frames


@router.websocket("/ws/video")
async def video_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time face detection streaming.

    Client sends:  { "frame": "<base64 image>", "session_id": "<uuid>" }
    Server sends:  { "face_detected": bool, "roi": {...}, "frame": "<base64>" }
    """
    await websocket.accept()
    frame_number = 0
    session_id = str(uuid.uuid4())

    print(f"Client connected — session: {session_id}")

    try:
        while True:
            data = await websocket.receive_json()            
            frame_b64 = data.get("frame")
            if not frame_b64:
                await websocket.send_json({"error": "no frame provided"})
                continue

            frame_number += 1

            # 2. decode base64 → PIL image
            try:
                img_bytes = base64.b64decode(frame_b64)
                pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            except Exception:
                await websocket.send_json({"error": "invalid frame data"})
                continue

            # 3. resize for performance (max 640px wide)
            pil_image = resize_frame(pil_image, max_width=640)

            # 4. run face detection
            roi = detect_face(pil_image)

            if roi is None:
                # no face — send back original frame
                await websocket.send_json({
                    "face_detected": False,
                    "roi": None,
                    "frame": image_to_base64(pil_image),
                    "frame_number": frame_number,
                    "session_id": session_id
                })
                continue

            # 5. draw bounding box
            annotated = draw_bounding_box(pil_image, roi)

            # 6. save ROI to DB every N frames only (performance)
            if frame_number % SAVE_EVERY_N_FRAMES == 0:
                await save_roi_to_db(session_id, frame_number, roi)
                
            # 7. send processed frame + roi back to client
            await websocket.send_json({
                "face_detected": True,
                "roi": roi,
                "frame": image_to_base64(annotated),
                "frame_number": frame_number,
                "session_id": session_id
            })

    except WebSocketDisconnect:
        print(f"Client disconnected — session: {session_id}, frames: {frame_number}")
    except Exception as e:
        print(f"Unexpected error in session {session_id}: {e}")


def resize_frame(image: Image.Image, max_width: int = 640) -> Image.Image:
    """Resize image keeping aspect ratio — avoids processing huge frames."""
    w, h = image.size
    if w <= max_width:
        return image
    ratio = max_width / w
    new_size = (max_width, int(h * ratio))
    return image.resize(new_size, Image.LANCZOS)


async def save_roi_to_db(session_id: str, frame_number: int, roi: dict):
    """Save ROI detection to PostgreSQL."""
    async with SessionLocal() as session:
        try:
            record = ROIDetection(
                session_id=session_id,
                frame_number=frame_number,
                x=roi["x"],
                y=roi["y"],
                width=roi["width"],
                height=roi["height"],
                confidence=roi["confidence"]
            )
            session.add(record)
            await session.commit()
        except Exception as e:
            print(f"DB save failed: {e}")
            await session.rollback()