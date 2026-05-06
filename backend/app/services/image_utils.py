import io
import base64
from PIL import Image, ImageDraw


def draw_bounding_box(pil_image: Image.Image, roi: dict) -> Image.Image:
    """
    Draws a rectangle around the detected face.
    Uses Pillow only — no OpenCV.

    roi dict must have: x, y, width, height
    """
    image = pil_image.copy()
    draw = ImageDraw.Draw(image)

    x = roi["x"]
    y = roi["y"]
    width = roi["width"]
    height = roi["height"]

    top_left = (x, y)
    bottom_right = (x + width, y + height)

    # draw green rectangle, 3px thick
    draw.rectangle(
        [top_left, bottom_right],
        outline=(0, 255, 0),
        width=3
    )

    # draw label above the box
    label = f"Face {roi['confidence'] * 100:.0f}%"
    draw.text((x, max(0, y - 15)), label, fill=(0, 255, 0))

    return image


def image_to_base64(pil_image: Image.Image) -> str:
    """
    Converts PIL image → base64 string.
    Frontend can display this directly in an <img> tag.
    """
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return encoded