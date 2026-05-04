import os
from PIL import Image, ImageEnhance

def enhance_for_visibility(image_path: str) -> str:
    """Enhance contrast and sharpness to improve visibility assessment down the road"""
    img = Image.open(image_path)
    
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    
    out_path = image_path.replace(".jpg", "_enhanced.jpg")
    img.save(out_path)
    return out_path


def get_visibility_images(stop_id: int, image_dir: str = "../data/images/main") -> list[str]:
    """Get N/S images from all three positions (orig, fwd, bwd) and enhance them"""
    stop_path = os.path.join(image_dir, str(stop_id))
    if not os.path.isdir(stop_path):
        return []
    
    target_suffixes = [
        f"{stop_id}_n.jpg",
        f"{stop_id}_s.jpg",
        f"{stop_id}_fwd_n.jpg",
        f"{stop_id}_fwd_s.jpg",
        f"{stop_id}_bwd_n.jpg",
        f"{stop_id}_bwd_s.jpg",
    ]
    
    paths = []
    for fname in target_suffixes:
        full_path = os.path.join(stop_path, fname)
        if os.path.exists(full_path):
            enhanced = enhance_for_visibility(full_path)
            paths.append(enhanced)
    
    return paths

def get_ada_images(stop_id: int, image_dir: str = "../data/images/main") -> list[str]:
    """E and W images show the curb cross-section best for ADA assessment"""
    stop_path = os.path.join(image_dir, str(stop_id))
    if not os.path.isdir(stop_path):
        return []
    
    target_files = [
        f"{stop_id}_e.jpg",
        f"{stop_id}_w.jpg",
    ]
    
    return [
        os.path.join(stop_path, fname)
        for fname in target_files
        if os.path.exists(os.path.join(stop_path, fname))
    ]

def get_original_images(stop_id: int, image_dir: str = "../data/images/main") -> list[str]:
    """Returns only the 4 original direction images (no fwd/bwd offsets)"""
    stop_path = os.path.join(image_dir, str(stop_id))
    if not os.path.isdir(stop_path):
        return []
    return [
        os.path.join(stop_path, f)
        for f in os.listdir(stop_path)
        if os.path.isfile(os.path.join(stop_path, f)) 
        and f.endswith(".jpg")
        and any(f.lower().endswith(f"_{d}.jpg") for d in ["n", "s", "e", "w"])
    ]

def get_n_s(stop_id: int, image_dir: str = "../data/images/main") -> list[str]:
    stop_path = os.path.join(image_dir, str(stop_id))
    
    if not os.path.isdir(stop_path):
        print(f"Warning: Folder for ID {stop_id} not found.")
        return []

    return [
        os.path.join(stop_path, f) 
        for f in os.listdir(stop_path) 
        if ("_n" in f.lower() or "_s" in f.lower()) and os.path.isfile(os.path.join(stop_path, f))
    ]

def get_obstruction_images(stop_id: int, image_dir: str = "../data/images/main") -> list[str]:
    """All 4 original directions enhanced — obstructions visible from any angle"""
    stop_path = os.path.join(image_dir, str(stop_id))
    if not os.path.isdir(stop_path):
        return []
    
    target_files = [
        f"{stop_id}_n.jpg",
        f"{stop_id}_s.jpg",
        f"{stop_id}_e.jpg",
        f"{stop_id}_w.jpg",
    ]
    
    paths = []
    for fname in target_files:
        full_path = os.path.join(stop_path, fname)
        if os.path.exists(full_path):
            enhanced = enhance_for_visibility(full_path)
            paths.append(enhanced)
    
    return paths