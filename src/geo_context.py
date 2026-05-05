import requests
from src.config import GOOGLE_API_KEY

def get_location_label(lat: float, lng: float) -> str:
    """Returns a human-readable location string"""
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY},
            timeout=8,
        )
        results = resp.json().get("results", [])
        if not results:
            return "Unknown Location"

        components = results[0]["address_components"]
        parts = {}
        for c in components:
            if "neighborhood" in c["types"]:
                parts["neighborhood"] = c["long_name"]
            elif "locality" in c["types"]:
                parts["city"] = c["long_name"]
            elif "administrative_area_level_1" in c["types"]:
                parts["state"] = c["short_name"]

        label = ", ".join(filter(None, [
            parts.get("neighborhood"),
            parts.get("city"),
            parts.get("state"),
        ]))
        return label or results[0]["formatted_address"]

    except Exception as e:
        print(f"  [geo_context] reverse geocode failed: {e}")
        return "Unknown Location"
