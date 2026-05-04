import time
import requests
from src.config import OVERPASS_HEADERS

def _overpass_query(query: str, retries: int = 3) -> list:
    for attempt in range(retries):
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": query},
            headers=OVERPASS_HEADERS
        )
        if response.status_code == 200 and response.text.strip():
            return response.json().get("elements", [])
        time.sleep(2 ** attempt)
    return []

def fetch_overpass_data(lat: float, lng: float) -> list:
    """Single batched Overpass call covering all criteria."""
    query = f"""
        [out:json];
        (
        node["railway"="level_crossing"](around:61,{lat},{lng});
        way["railway"="rail"](around:91,{lat},{lng});
        way["highway"="motorway_link"](around:76,{lat},{lng});
        way["highway"="trunk_link"](around:76,{lat},{lng});
        node["highway"="traffic_signals"](around:30,{lat},{lng});
        way["highway"="motorway"](around:15,{lat},{lng});
        way["highway"="trunk"](around:15,{lat},{lng});
        way["lanes"~"^([3-9]|[1-9][0-9]+)$"](around:15,{lat},{lng});
        way["turn:lanes"~"right"](around:30,{lat},{lng});
        way["turn:lanes:forward"~"right"](around:30,{lat},{lng});
        way["turn:lanes:backward"~"right"](around:30,{lat},{lng});
        way["natural"="water"](around:46,{lat},{lng});
        way["natural"="bay"](around:46,{lat},{lng});
        way["natural"="coastline"](around:46,{lat},{lng});
        way["natural"="wetland"](around:46,{lat},{lng});
        way["waterway"~"river|stream|canal|lake"](around:46,{lat},{lng});
        way["landuse"="reservoir"](around:46,{lat},{lng});
        relation["natural"="water"](around:46,{lat},{lng});
        way["barrier"~"fence|wall|guardrail|railing"](around:46,{lat},{lng});
        node["highway"="turning_circle"](around:91,{lat},{lng});
        node["highway"="turning_loop"](around:91,{lat},{lng});
        node["noexit"="yes"](around:91,{lat},{lng});
        way["cycleway"~"lane|track"](around:15,{lat},{lng});
        way["cycleway:right"="lane"](around:15,{lat},{lng});
        way["cycleway:left"="lane"](around:15,{lat},{lng});
        way["highway"="cycleway"](around:15,{lat},{lng});
        );
        out body;
    """
    return _overpass_query(query)