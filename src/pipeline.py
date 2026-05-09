import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.models import Location, CriterionResult
from src.overpass import fetch_overpass_data
from src.street_view import get_street_view_image
from src.checks.api_checks import (
    check_railroad,
    check_slope,
    check_freeway_ramp,
    check_traffic_signal,
    check_divided_highway,
    check_right_turn_lane,
    check_uturn,
    check_bike_lane,
)
from src.checks.llm_checks import (
    check_sidewalk,
    check_waiting_area,
    check_visibility,
    check_ada,
    check_obstructions,
    check_water_body,
)
from src.scoring import compute_score
from src.roads import reverse_geocode


def run_all_llm_checks(stop_id: int | str, elements: list, set_name: str = "main") -> list[CriterionResult]:
    """Run all VLM-based checks in parallel. max_workers=4 to respect LM Studio limits."""
    checks = [
        lambda: check_sidewalk(stop_id, set_name),
        lambda: check_waiting_area(stop_id, set_name),
        lambda: check_visibility(stop_id, set_name),
        lambda: check_ada(stop_id, set_name),
        lambda: check_obstructions(stop_id, set_name),
        lambda: check_water_body(stop_id, elements, set_name),
    ]

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fn): fn for fn in checks}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"  LLM check failed: {e}")
    return results


def evaluate_location(
    loc: Location,
    stop_id: int | str,
    set_name: str = "main",
) -> dict:
    """
    Full evaluation pipeline for a single location.
    Images must already exist on disk at images/{set_name}/{stop_id}/ before calling this.

    Returns:
        {
            "stop_id": ...,
            "snapped_lat": ...,
            "snapped_lng": ...,
            "results": [CriterionResult, ...]
        }
    """
    print(f"\n── Evaluating stop {stop_id} ({loc.lat:.5f}, {loc.lng:.5f}) ──")

    elements = fetch_overpass_data(loc.lat, loc.lng)

    api_results = [
        check_railroad(loc.lat, loc.lng, elements),
        check_slope(loc),
        check_freeway_ramp(elements),
        check_traffic_signal(elements),
        check_divided_highway(elements),
        check_right_turn_lane(elements),
        check_uturn(elements),
        check_bike_lane(elements),
    ]

    llm_results = run_all_llm_checks(stop_id, elements, set_name)

    all_results = api_results + llm_results
    scoring = compute_score(all_results)

    return {
        "stop_id": stop_id,
        "lat": loc.lat,
        "lng": loc.lng,
        "snapped_lat": loc.lat,
        "snapped_lng": loc.lng,
        "score":   scoring["score"],
        "verdict": scoring["verdict"],
        "failures": scoring["failures"],
        "results": all_results,
    }

def evaluate_from_coordinates(lat: float, lng: float, set_name: str = "web") -> dict:
    """
    Entry point for the web app — takes raw lat/lng, handles everything.

    1. Fetches Street View images and snaps to road.
    2. Generates a unique job_id as the folder name.
    3. Runs full evaluation.

    Returns same shape as evaluate_location, plus job_id for the frontend
    to reference images.
    """
    job_id = str(uuid.uuid4())[:8]

    print(f"  fetching Street View images → {set_name}/{job_id}/")
    snapped_lat, snapped_lng = get_street_view_image(lat, lng, job_id, set_name)

    if snapped_lat is None:
        return {
            "stop_id": job_id,
            "snapped_lat": lat,
            "snapped_lng": lng,
            "results": [],
            "error": "No Street View coverage at this location",
        }

    loc = Location(lat=snapped_lat, lng=snapped_lng)
    
    geo = reverse_geocode(snapped_lat, snapped_lng)
    
    result = evaluate_location(loc, job_id, set_name)
    result["job_id"] = job_id
    result["city"]    = geo["city"]
    result["state"]   = geo["state"]
    result["country"] = geo["country"]
    result["lat"]     = lat
    result["lng"]     = lng
    return result
