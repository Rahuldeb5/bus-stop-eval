import requests
from src.config import GOOGLE_API_KEY
from src.models import Location
from src.utils import haversine_distance, calculate_bearing, offset_along_bearing

def get_road_bearing(lat: float, lng: float) -> tuple[float, float, float]:
    road_offset = 0.00018   # ~20 meters
    
    probes = {
        "origin": (lat, lng),
        "north": (lat + road_offset, lng),
        "south": (lat - road_offset, lng),
        "east": (lat, lng + road_offset),
        "west": (lat, lng - road_offset)
    }
    
    path = "|".join(f"{lat},{lng}" for lat, lng in probes.values())
    url = "https://roads.googleapis.com/v1/snapToRoads"
    params = {"path": path, "interpolate": "false", "key": GOOGLE_API_KEY}
    snapped = requests.get(url, params=params).json().get("snappedPoints", [])
    
    if len(snapped) < 2:
        print("Length snapped < 2 — skipping")
        return None, None, None
    
    anchor = snapped[0]
    anchor_id = anchor.get("placeId")
    anchor_loc = anchor.get("location")
    
    same_road = [
        p for p in snapped[1:] if p.get("placeId") == anchor_id
    ]
    
    if not same_road:
        print("Not same road — skipping")
        return None, None, None
    
    best = max(same_road, key=lambda p: haversine_distance(anchor_loc, p.get("location")))
    
    if haversine_distance(anchor_loc, best["location"]) < 1:
        print("Max distance < 1 — skipping")
        return None, None, None
    
    bearing = calculate_bearing(anchor_loc, best.get("location"))
    
    return bearing, anchor_loc["latitude"], anchor_loc["longitude"]

def get_elevations(points: list[tuple]) -> list[float]:
    locations = "|".join(f"{lat},{lng}" for lat, lng in points)
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "locations": locations,
        "key": GOOGLE_API_KEY
    }
    results = requests.get(url, params=params).json()["results"]
    return [r["elevation"] for r in results]

def get_speed_limit(loc: Location) -> int | None:
    url = "https://roads.googleapis.com/v1/speedLimits"
    params = {
        "path": f"{loc.lat},{loc.lng}",
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params).json()
    speed_limits = response.get("speedLimits", [])
    
    if not speed_limits:
        return None
    
    return speed_limits[0].get("speedLimit")
