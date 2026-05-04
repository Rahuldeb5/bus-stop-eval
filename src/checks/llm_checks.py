from src.models import CriterionResult, Importance
from src.config import load_prompt
from src.images import (
    get_original_images,
    get_visibility_images,
    get_ada_images,
    get_obstruction_images,
)
from src.llm import evaluate_with_voting, evaluate_single_image
from src.overpass import _overpass_query

def check_sidewalk(stop_id: int) -> CriterionResult:
    """
    Check for sidewalk or safe walking path to the stop.
    Uses N/S images from all three positions (origin, fwd, bwd).
    Any direction showing no path is evidence of failure.
    """
    image_paths = get_original_images(stop_id)
    prompt = load_prompt("sidewalk")
    result = evaluate_with_voting(image_paths, prompt)

    return CriterionResult(
        criterion="sidewalk",
        passed=result["passed"],
        importance=Importance.LOW,
        notes=result["reasoning"],
    )

def check_waiting_area(stop_id: int) -> CriterionResult:
    """
    Check for an adequate waiting area at the stop.
    Uses original 4-direction images.
    """
    image_paths = get_original_images(stop_id)
    prompt = load_prompt("waiting_area")
    result = evaluate_with_voting(image_paths, prompt)

    return CriterionResult(
        criterion="waiting_area",
        passed=result["passed"],
        importance=Importance.MEDIUM,
        notes=result["reasoning"],
    )

def check_visibility(stop_id: int) -> CriterionResult:
    """
    Check sight lines along the road in both directions.
    Uses enhanced N/S images from origin, fwd, and bwd positions.
    """
    image_paths = get_visibility_images(stop_id)
    prompt = load_prompt("visibility")
    result = evaluate_with_voting(image_paths, prompt)

    return CriterionResult(
        criterion="visibility",
        passed=result["passed"],
        importance=Importance.CRITICAL,
        notes=result["reasoning"],
    )

def check_ada(stop_id: int) -> CriterionResult:
    """
    Check for ADA-accessible curb cuts and landing area.
    Uses E/W images which show the curb cross-section best.
    """
    image_paths = get_ada_images(stop_id)
    prompt = load_prompt("ada")
    result = evaluate_with_voting(image_paths, prompt)

    return CriterionResult(
        criterion="ada",
        passed=result["passed"],
        importance=Importance.MEDIUM,
        notes=result["reasoning"],
    )

def check_obstructions(stop_id: int) -> CriterionResult:
    """
    Check for physical obstructions at the stop (poles, vegetation, parked cars, etc).
    Uses all 4 original directions — obstructions can appear from any angle.
    """
    image_paths = get_obstruction_images(stop_id)
    prompt = load_prompt("obstructions")
    result = evaluate_with_voting(image_paths, prompt)

    return CriterionResult(
        criterion="obstructions",
        passed=result["passed"],
        importance=Importance.MEDIUM,
        notes=result["reasoning"],
    )

def check_water_body(stop_id: int, elements: list) -> CriterionResult:
    """
    Check for water hazard within 150ft with no physical barrier.

    Logic:
    1. Check pre-fetched Overpass elements for water features.
    2. If OSM finds nothing, use VLM to check imagery (catches unmapped water).
    3. If water is detected by either source, check for a barrier via OSM + VLM.
    4. Barrier confirmed → pass. No barrier → fail. Inconclusive → None (human review).
    """
    water_tags = {
        "natural": {"water", "bay", "coastline", "wetland"},
        "waterway": {"river", "stream", "canal", "lake"},
        "landuse": {"reservoir"},
    }

    water_elements = [
        e for e in elements
        if any(
            e.get("tags", {}).get(key) in vals
            for key, vals in water_tags.items()
        )
    ]
    water_detected = len(water_elements) > 0

    if not water_detected:
        print("  OSM clear — checking VLM for water...", end=" ", flush=True)
        image_paths = get_original_images(stop_id)
        detect_results = [
            evaluate_single_image(p, load_prompt("water_detect"))
            for p in image_paths
        ]
        high_certainty = [
            r for r in detect_results
            if r.get("passed") is not None and r.get("certainty", 0) >= 0.6
        ]

        if not high_certainty:
            print("✅")
            return CriterionResult(
                criterion="water_body",
                passed=True,
                notes="No water body found near stop;",
            )

        best_detect = max(high_certainty, key=lambda r: r.get("certainty", 0))
        if not best_detect["passed"]:
            print("✅")
            return CriterionResult(
                criterion="water_body",
                passed=True,
                notes="No water body detected via OSM or imagery;",
            )

        print("⚠️  VLM detected water OSM missed")
        water_detected = True

    print("  water nearby — checking barrier...", end=" ", flush=True)

    barrier_elements = [
        e for e in elements
        if e.get("tags", {}).get("barrier") in {"fence", "wall", "guardrail", "railing"}
    ]
    osm_barrier_hint = len(barrier_elements) > 0

    image_paths = get_original_images(stop_id)
    barrier_results = [
        evaluate_single_image(p, load_prompt("water_barrier"))
        for p in image_paths
    ]
    high_certainty = [
        r for r in barrier_results
        if r.get("passed") is not None and r.get("certainty", 0) >= 0.6
    ]

    if high_certainty:
        best = max(high_certainty, key=lambda r: r.get("certainty", 0))
        if best["passed"]:
            print("✅ barrier confirmed")
            return CriterionResult(
                criterion="water_body",
                passed=True,
                notes=f"Water body nearby but barrier detected — {best['reasoning']};",
            )
        print("❌ HIGH")
        return CriterionResult(
            criterion="water_body",
            passed=False,
            importance=Importance.HIGH,
            notes=f"Water body within 150ft with no barrier detected — {best['reasoning']};",
        )

    if osm_barrier_hint:
        print("⚠️  inconclusive — OSM suggests barrier but unconfirmed")
        return CriterionResult(
            criterion="water_body",
            passed=None,
            importance=Importance.HIGH,
            notes="Water body within 150ft — OSM suggests barrier nearby but not visually confirmed, human review required;",
        )

    print("⚠️  inconclusive")
    return CriterionResult(
        criterion="water_body",
        passed=None,
        importance=Importance.HIGH,
        notes="Water body within 150ft — barrier not confirmable from OSM or imagery, human review required;",
    )
