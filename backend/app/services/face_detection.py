import numpy as np
from PIL import Image

# import ONLY face_detection — avoids mediapipe pulling in cv2 drawing utils
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
detector = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)


def detect_face(pil_image: Image.Image) -> dict | None:
    """
    Takes a PIL Image, runs MediaPipe face detection.
    Returns bounding box dict or None if no face found.
    No OpenCV used — PIL + numpy only.
    """
    img_w, img_h = pil_image.size

    # PIL → numpy RGB array
    rgb_array = np.array(pil_image.convert("RGB"), dtype=np.uint8)

    results = detector.process(rgb_array)

    if not results.detections:
        return None

    # pick first detection (problem says only one face)
    detection = results.detections[0]
    confidence = detection.score[0]

    # MediaPipe returns relative coords (0.0 → 1.0), also convert to actual pixel vals
    bbox = detection.location_data.relative_bounding_box

    x = max(0, int(bbox.xmin * img_w))
    y = max(0, int(bbox.ymin * img_h))
    width = min(img_w - x, int(bbox.width * img_w))
    height = min(img_h - y, int(bbox.height * img_h))

    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "confidence": round(float(confidence), 4)
    }