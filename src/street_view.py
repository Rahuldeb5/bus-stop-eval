import os
import time
import requests
import pandas as pd
from src.config import GOOGLE_API_KEY, IMAGE_DIR
from src.roads import get_road_bearing
from src.utils import offset_along_bearing

def check_street_view_coverage(lat: float, lng: float) -> bool:
    url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {"location": f"{lat:.6f},{lng:.6f}", "source": "outdoor", "key": GOOGLE_API_KEY}
    return requests.get(url, params=params).json().get("status") == "OK"

def _capture_directions(lat: float, lng: float, bearing: float, img_id: int, set_name: str, suffix: str):
    """Capture 4 directional images at a given position. Suffix is '' for origin, 'fwd'/'bwd' for offsets."""
    directions = ["n", "e", "s", "w"]
    path = os.path.join(IMAGE_DIR.replace("main", set_name), str(img_id))
    os.makedirs(path, exist_ok=True)

    for i, direction in enumerate(directions):
        heading = (bearing + 90 * i) % 360
        params = {
            "size": "640x640",
            "location": f"{lat:.6f},{lng:.6f}",
            "heading": round(heading, 1),
            "fov": 100,
            "pitch": 0,
            "source": "outdoor",
            "key": GOOGLE_API_KEY
        }
        response = requests.get("https://maps.googleapis.com/maps/api/streetview", params=params)
        fname = f"{img_id}_{suffix}_{direction}.jpg" if suffix else f"{img_id}_{direction}.jpg"
        with open(os.path.join(path, fname), "wb") as f:
            f.write(response.content)

def get_street_view_image(lat: float, lng: float, img_id: int, set_name: str) -> tuple[float, float] | tuple[None, None]:
    if not check_street_view_coverage(lat, lng):
        print("No outdoor coverage — skipping")
        return None, None

    bearing, snapped_lat, snapped_lng = get_road_bearing(lat, lng)
    if bearing is None:
        print("Could not get road bearing — skipping")
        return None, None

    print(f"Snapped to {snapped_lat:.6f},{snapped_lng:.6f} | bearing={bearing:.1f}°")
    _capture_directions(snapped_lat, snapped_lng, bearing, img_id, set_name, suffix="")
    return snapped_lat, snapped_lng

def collect_offset_images(manifest_path: str, set_name: str, offset_m: int = 12):
    df = pd.read_csv(manifest_path)

    for _, row in df.iterrows():
        img_id = int(row["id"])
        lat, lng = row["snapped_lat"], row["snapped_lng"]
        print(f"\n[{img_id}/{len(df)}] {row['city']}, {row['state']}")

        bearing, snapped_lat, snapped_lng = get_road_bearing(lat, lng)
        if bearing is None:
            print("  Could not get bearing — skipping")
            continue

        fwd_lat, fwd_lng = offset_along_bearing(snapped_lat, snapped_lng, bearing, offset_m)
        bwd_lat, bwd_lng = offset_along_bearing(snapped_lat, snapped_lng, (bearing + 180) % 360, offset_m)
        print(f"  bearing={bearing:.1f}° | fwd=({fwd_lat:.6f},{fwd_lng:.6f}) | bwd=({bwd_lat:.6f},{bwd_lng:.6f})")

        _capture_directions(fwd_lat, fwd_lng, bearing, img_id, set_name, suffix="fwd")
        _capture_directions(bwd_lat, bwd_lng, bearing, img_id, set_name, suffix="bwd")
        time.sleep(0.5)