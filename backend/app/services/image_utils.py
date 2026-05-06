import io
import base64
from PIL import Image, ImageDraw

MAX_OUTPUT_WIDTH = 640  # for browser stability

def draw_bounding_box(pil_image: Image.Image, roi: dict) -> Image.Image:
    """
    Draw safe bounding box.
    """
    image = pil_image.copy()
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size

    x = max(0, min(roi["x"], img_w - 1))
    y = max(0, min(roi["y"], img_h - 1))
    width = max(1, min(roi["width"], img_w - x))
    height = max(1, min(roi["height"], img_h - y))

    draw.rectangle(
        [(x, y), (x + width, y + height)],
        outline=(0, 255, 0),
        width=3
    )
    label = f"Face {roi['confidence'] * 100:.0f}%"
    text_y = max(5, y - 20)
    draw.text((x, text_y), label, fill=(0, 255, 0))
    return image


def image_to_base64(pil_image: Image.Image) -> str:
    """
    Resize + compress image → base64 (browser safe).
    """

    img_w, img_h = pil_image.size
    if img_w > MAX_OUTPUT_WIDTH:
        scale = MAX_OUTPUT_WIDTH / img_w
        new_h = int(img_h * scale)
        pil_image = pil_image.resize((MAX_OUTPUT_WIDTH, new_h))

    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG", quality=70, optimize=True)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return encoded