import base64
import os
from typing import Any
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
import base64

def is_base64_image(data: str) -> bool:
    if not isinstance(data, str):
        return False
    if data.startswith("data:image/"):
        return True
    try:
        decoded = base64.b64decode(data, validate=True)
        return decoded[:4] in [b'\x89PNG', b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1']  # PNG/JPEG headers
    except Exception:
        return False


unique_image_filename_id = 0
def get_unique_image_filename_id() -> str:
    global unique_image_filename_id
    unique_image_filename_id += 1
    return f"{unique_image_filename_id:06}"

unique_image_filename_id = 0
def reset_unique_image_filename_id(value:int = 0) -> str:
    global unique_image_filename_id
    unique_image_filename_id = value

def save_base64_image(data: str, output_dir="images", images_tag:str = None) -> str:
    os.makedirs(output_dir, exist_ok=True)

    if data.startswith("data:image/"):
        header, b64data = data.split(",", 1)
        ext = header.split("/")[1].split(";")[0]
    else:
        b64data = data
        ext = "png"  # fallback

    try:
        image_data = base64.b64decode(b64data)
    except Exception as e:
        raise ValueError("Invalid base64 image data") from e

    filename = f"{get_unique_image_filename_id()}-{images_tag}.{ext}" if images_tag else f"{get_unique_image_filename_id()}.{ext}"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(image_data)

    # the returned filepath is only the file name - no folder - so we can copy the folder
    return os.path.basename(filepath)

def save_pil_image(img: Image.Image, output_dir="images", images_tag:str = None) -> str:
    os.makedirs(output_dir, exist_ok=True)
    ext = "png"
    base_filename = f"{get_unique_image_filename_id()}-{images_tag}.{ext}" if images_tag else f"{get_unique_image_filename_id()}.{ext}"
    filepath = os.path.join(output_dir, base_filename)
    img.save(filepath)
    return base_filename


def scan_and_replace_images(obj: Any, output_dir="images", images_tag:str = None) -> Any:
    if isinstance(obj, BaseModel):
        new_data = {}
        for k, v in obj.__dict__.items():
            new_data[k] = scan_and_replace_images(v, output_dir, images_tag = images_tag)
        # return new_data
        return obj.__class__(**new_data)  # <-- Reconstruct the model instance

    elif isinstance(obj, dict):
        return {k: scan_and_replace_images(v, output_dir, images_tag = images_tag) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [scan_and_replace_images(item, output_dir, images_tag = images_tag) for item in obj]

    elif isinstance(obj, bytes):
        try:
            decoded = obj.decode("utf-8")
            if is_base64_image(decoded):
                return save_base64_image(decoded, output_dir, images_tag = images_tag)
            return decoded  # <-- safe decoded text, even if not an image
        except UnicodeDecodeError:
            # fallback: encode binary bytes to base64 string
            decoded = base64.b64encode(obj).decode("utf-8")
            if is_base64_image(decoded):
                return save_base64_image(decoded, output_dir, images_tag = images_tag)
            else:
                return decoded

    elif isinstance(obj, str) and is_base64_image(obj):
        return save_base64_image(obj, output_dir, images_tag = images_tag)

    elif isinstance(obj, Image.Image):
        return save_pil_image(obj, output_dir, images_tag = images_tag)

    else:
        return obj
