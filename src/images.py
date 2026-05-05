import os
from PIL import Image, ImageEnhance
from src.config import IMAGE_DIR

def _stop_path(stop_id: int | str, set_name: str) -> str:
    return os.path.join(IMAGE_DIR, set_name, str(stop_id))

def enhance_for_visibility(image_path: str) -> str:
    img = Image.open(image_path)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    out_path = image_path.replace(".jpg", "_enhanced.jpg")
    img.save(out_path)
    return out_path

def get_original_images(stop_id: int | str, set_name: str = "main") -> list[str]:
    stop_path = _stop_path(stop_id, set_name)
    if not os.path.isdir(stop_path):
        print(f"  ⚠️  no image folder at {stop_path}")
        return []
    return [
        os.path.join(stop_path, f)
        for f in os.listdir(stop_path)
        if os.path.isfile(os.path.join(stop_path, f))
        and any(f.lower().endswith(f"_{d}.jpg") for d in ["n", "s", "e", "w"])
    ]

def get_visibility_images(stop_id: int | str, set_name: str = "main") -> list[str]:
    stop_path = _stop_path(stop_id, set_name)
    if not os.path.isdir(stop_path):
        return []
    target_suffixes = [f"{stop_id}_{d}.jpg" for d in ["n", "s", "fwd_n", "fwd_s", "bwd_n", "bwd_s"]]
    paths = []
    for fname in target_suffixes:
        full_path = os.path.join(stop_path, fname)
        if os.path.exists(full_path):
            paths.append(enhance_for_visibility(full_path))
    return paths

def get_ada_images(stop_id: int | str, set_name: str = "main") -> list[str]:
    stop_path = _stop_path(stop_id, set_name)
    if not os.path.isdir(stop_path):
        return []
    return [
        os.path.join(stop_path, f"{stop_id}_{d}.jpg")
        for d in ["e", "w"]
        if os.path.exists(os.path.join(stop_path, f"{stop_id}_{d}.jpg"))
    ]

def get_obstruction_images(stop_id: int | str, set_name: str = "main") -> list[str]:
    stop_path = _stop_path(stop_id, set_name)
    if not os.path.isdir(stop_path):
        return []
    paths = []
    for d in ["n", "s", "e", "w"]:
        full_path = os.path.join(stop_path, f"{stop_id}_{d}.jpg")
        if os.path.exists(full_path):
            paths.append(enhance_for_visibility(full_path))
    return paths
