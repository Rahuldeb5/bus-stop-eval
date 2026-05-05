import os
import pandas as pd
from collections import defaultdict
from src.config import DATA_DIR, FRA_PATH
from src.utils import haversine_distance

CELL_SIZE = 0.01

_fra_df = None
_fra_index = None

def _ensure_fra_loaded():
    global _fra_df, _fra_index
    if _fra_df is None:
        _fra_df = _load_fra_crossings(os.path.join(DATA_DIR, FRA_PATH))
        _fra_index = _build_spatial_index(_fra_df)

def _load_fra_crossings(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    return df[
        (df["LATITUDE"] > 24) & (df["LATITUDE"] < 50) &
        (df["LONGITUD"] > -125) & (df["LONGITUD"] < -65)
    ].reset_index(drop=True)

def _build_spatial_index(df: pd.DataFrame) -> dict:
    index = defaultdict(list)
    for i, row in df.iterrows():
        cell_lat = int(row["LATITUDE"] / CELL_SIZE)
        cell_lng = int(row["LONGITUD"] / CELL_SIZE)
        index[(cell_lat, cell_lng)].append(i)
    return index

def query_fra_crossings(lat: float, lng: float, radius_m: float = 61) -> list:
    """Returns FRA at-grade crossings within radius_m of the given point."""
    _ensure_fra_loaded()

    radius_deg = radius_m / 111320
    cell_lat_min = int((lat - radius_deg) / CELL_SIZE)
    cell_lat_max = int((lat + radius_deg) / CELL_SIZE)
    cell_lng_min = int((lng - radius_deg) / CELL_SIZE)
    cell_lng_max = int((lng + radius_deg) / CELL_SIZE)

    candidates = []
    for clat in range(cell_lat_min, cell_lat_max + 1):
        for clng in range(cell_lng_min, cell_lng_max + 1):
            candidates.extend(_fra_index.get((clat, clng), []))

    results = []
    for idx in candidates:
        row = _fra_df.iloc[idx]
        dist = haversine_distance(
            {"latitude": lat, "longitude": lng},
            {"latitude": row["LATITUDE"], "longitude": row["LONGITUD"]}
        )
        if dist <= radius_m:
            results.append({
                "crossing_id": row["CROSSING"],
                "highway": row["STREET"],
                "railroad": row["RAILROAD"],
                "type": row["POSXING"],
                "distance_m": round(dist, 1)
            })
    return results
