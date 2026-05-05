import math

EARTH_RADIUS_METERS = 6_371_000

def haversine_distance(loc1: dict, loc2: dict) -> float:
    """
    Calculate the great-circle distance in meters between two points.
    
    Args:
        loc1: {"latitude": float, "longitude": float}
        loc2: {"latitude": float, "longitude": float}
    
    Returns:
        Distance in meters.
    """
    
    phi1 = math.radians(loc1["latitude"])
    phi2 = math.radians(loc2["latitude"])
    dphi = math.radians(loc2["latitude"] - loc1["latitude"])
    dlambda = math.radians(loc2["longitude"] - loc1["longitude"])

    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    
    return EARTH_RADIUS_METERS * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def calculate_bearing(loc1: dict, loc2: dict) -> float:
    """
    Calculate the compass bearing in degrees (0-360) from loc1 to loc2.
    
    Args:
        loc1: {"latitude": float, "longitude": float}
        loc2: {"latitude": float, "longitude": float}
    
    Returns:
        Bearing in degrees, where 0 = North, 90 = East, 180 = South, 270 = West.
    """
    phi1 = math.radians(loc1["latitude"])
    phi2 = math.radians(loc2["latitude"])
    dlambda = math.radians(loc2["longitude"] - loc1["longitude"])

    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)

    return (math.degrees(math.atan2(y, x)) + 360) % 360

def offset_along_bearing(lat, lng, bearing_deg, distance_m):
    """
    Returns a new lat/lng point that is distance_m meters
    away from the original point in the direction of bearing_deg
    """

    bearing_rad = math.radians(bearing_deg)
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)

    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_m / EARTH_RADIUS_METERS) +
        math.cos(lat_rad) * math.sin(distance_m / EARTH_RADIUS_METERS) * math.cos(bearing_rad)
    )
    new_lng_rad = lng_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_m / EARTH_RADIUS_METERS) * math.cos(lat_rad),
        math.cos(distance_m / EARTH_RADIUS_METERS) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )

    return math.degrees(new_lat_rad), math.degrees(new_lng_rad)
