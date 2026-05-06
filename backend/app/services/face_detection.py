import numpy as np
from PIL import Image
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
detector = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)
MAX_WIDTH = 640  # for stability

def detect_face(pil_image: Image.Image) -> dict | None:
    """
    Detect face with resizing for stability.
    Returns ROI in ORIGINAL image scale.
    """

    original_w, original_h = pil_image.size
    scale = 1.0

    if original_w > MAX_WIDTH:
        scale = MAX_WIDTH / original_w
        resized_w = MAX_WIDTH
        resized_h = int(original_h * scale)
        pil_image = pil_image.resize((resized_w, resized_h))
    else:
        resized_w, resized_h = original_w, original_h
    rgb_array = np.array(pil_image.convert("RGB"), dtype=np.uint8)
    results = detector.process(rgb_array)

    if not results.detections:
        return None

    detection = results.detections[0]
    confidence = float(detection.score[0])
    bbox = detection.location_data.relative_bounding_box
  
    x = int(bbox.xmin * resized_w)
    y = int(bbox.ymin * resized_h)
    width = int(bbox.width * resized_w)
    height = int(bbox.height * resized_h)

    x = max(0, min(x, resized_w - 1))
    y = max(0, min(y, resized_h - 1))
    width = max(1, min(width, resized_w - x))
    height = max(1, min(height, resized_h - y))

    if scale != 1.0:
        inv = 1 / scale
        x = int(x * inv)
        y = int(y * inv)
        width = int(width * inv)
        height = int(height * inv)

    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "confidence": round(confidence, 4)
    }