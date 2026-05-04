from src.models import Location, CriterionResult, Importance
from src.roads import get_road_bearing, get_elevations
from src.fra import query_fra_crossings
from src.utils import offset_along_bearing

def check_railroad(lat: float, lng: float, elements: list) -> CriterionResult:
    """
    FRA local CSV (61m / 200ft) → CRITICAL if hit.
    OSM rail ways (91m / 300ft) → HIGH if hit without FRA crossing.
    lat/lng passed explicitly because FRA lookup is not Overpass-based.
    """
    osm_tracks = [
        e for e in elements
        if e.get("type") == "way" and e.get("tags", {}).get("railway") == "rail"
    ]
    fra_crossings = query_fra_crossings(lat, lng, radius_m=61)

    fra_hit = len(fra_crossings) > 0
    osm_hit = len(osm_tracks) > 0

    if not fra_hit and not osm_hit:
        print("✅")
        return CriterionResult(criterion="railroad", passed=True)

    notes = ""
    if fra_hit:
        closest = min(fra_crossings, key=lambda c: c["distance_m"])
        notes += (
            f"FRA at-grade crossing within 200ft "
            f"({closest['crossing_id']} on {closest['highway']}, {closest['distance_m']}m);"
        )
    if osm_hit:
        notes += f"OSM railroad tracks within 300ft ({len(osm_tracks)} way(s));"

    print("❌ CRITICAL" if fra_hit else "❌ HIGH")
    return CriterionResult(
        criterion="railroad",
        passed=False,
        importance=Importance.CRITICAL if fra_hit else Importance.HIGH,
        notes=notes,
    )

def check_slope(loc: Location) -> CriterionResult:
    """
    Road grade must be ≤ 10%.
    Samples elevation 100m forward and backward along the snapped road bearing.
    Still takes loc (not elements) because it calls Roads + Elevation APIs, not Overpass.
    """
    bearing, lat1, lng1 = get_road_bearing(loc.lat, loc.lng)

    if bearing is None:
        return CriterionResult(
            criterion="slope",
            passed=True,
            importance=None,
            notes="Could not determine road bearing — slope check skipped",
        )

    lat_fwd, lng_fwd = offset_along_bearing(lat1, lng1, bearing, 100)
    lat_bwd, lng_bwd = offset_along_bearing(lat1, lng1, (bearing + 180) % 360, 100)

    elev_bwd, elev_anchor, elev_fwd = get_elevations([
        (lat_bwd, lng_bwd),
        (lat1, lng1),
        (lat_fwd, lng_fwd),
    ])

    grade_fwd = abs(elev_fwd - elev_anchor) / 100 * 100
    grade_bwd = abs(elev_bwd - elev_anchor) / 100 * 100
    grade = max(grade_fwd, grade_bwd)
    passed = grade <= 10.0

    print(f"  grade={grade:.1f}%", "✅" if passed else "❌ CRITICAL")
    return CriterionResult(
        criterion="slope",
        passed=passed,
        importance=None if passed else Importance.CRITICAL,
        notes=f"Grade is {grade:.1f}% — {'within' if passed else 'exceeds'} 10% threshold",
    )

def check_freeway_ramp(elements: list) -> CriterionResult:
    """Stop must not be within 250ft of a motorway or trunk ramp."""
    ramps = [
        e for e in elements
        if e.get("tags", {}).get("highway") in ("motorway_link", "trunk_link")
    ]

    if not ramps:
        return CriterionResult(criterion="freeway_ramp", passed=True)

    return CriterionResult(
        criterion="freeway_ramp",
        passed=False,
        importance=Importance.HIGH,
        notes=f"Found {len(ramps)} freeway/trunk ramp(s) within 250ft of stop;",
    )

def check_traffic_signal(elements: list) -> CriterionResult:
    """Prefer stops within 100ft of a traffic control signal."""
    signals = [
        e for e in elements
        if e.get("type") == "node" and e.get("tags", {}).get("highway") == "traffic_signals"
    ]

    if signals:
        return CriterionResult(
            criterion="traffic_signal",
            passed=True,
            notes=f"Traffic control signal found within 100ft ({len(signals)} node(s));",
        )

    return CriterionResult(
        criterion="traffic_signal",
        passed=False,
        importance=Importance.LOW,
        notes="No traffic control signal found within 100ft;",
    )

def check_divided_highway(elements: list) -> CriterionResult:
    """Stop should not be on a divided highway or road with 3+ lanes."""
    divided = [
        e for e in elements
        if e.get("tags", {}).get("highway") in ("motorway", "trunk")
    ]
    multilane = [
        e for e in elements
        if int(e.get("tags", {}).get("lanes", 0) or 0) >= 3
    ]

    if not divided and not multilane:
        return CriterionResult(criterion="divided_highway", passed=True)

    types = []
    if divided:
        types.append("divided highway")
    if multilane:
        max_lanes = max(int(e.get("tags", {}).get("lanes", 0) or 0) for e in multilane)
        types.append(f"multi-lane roadway ({max_lanes} lanes)")

    print("❌ HIGH")
    return CriterionResult(
        criterion="divided_highway",
        passed=False,
        importance=Importance.HIGH,
        notes=f"Stop is located on a {' and '.join(types)};",
    )

def check_right_turn_lane(elements: list) -> CriterionResult:
    """Stop must not be within 100ft of a dedicated right turn lane."""
    turn_lanes = [
        e for e in elements
        if any(
            "right" in (e.get("tags", {}).get(key) or "")
            for key in ("turn:lanes", "turn:lanes:forward", "turn:lanes:backward")
        )
    ]

    if not turn_lanes:
        return CriterionResult(
            criterion="right_turn_lane",
            passed=True,
            notes="No right turn lane found within 100ft;",
        )

    return CriterionResult(
        criterion="right_turn_lane",
        passed=False,
        importance=Importance.HIGH,
        notes=f"Stop is within 100ft of a right turn lane ({len(turn_lanes)} way(s));",
    )

def check_uturn(elements: list) -> CriterionResult:
    """Bus must not need to U-turn or back up to serve the stop (300ft radius)."""
    turning_circles = [
        e for e in elements
        if e.get("type") == "node" and e.get("tags", {}).get("highway") == "turning_circle"
    ]
    turning_loops = [
        e for e in elements
        if e.get("type") == "node" and e.get("tags", {}).get("highway") == "turning_loop"
    ]
    dead_ends = [
        e for e in elements
        if e.get("type") == "node" and e.get("tags", {}).get("noexit") == "yes"
    ]

    if not turning_circles and not turning_loops and not dead_ends:
        return CriterionResult(criterion="uturn", passed=True)

    types = []
    if turning_circles:
        types.append("cul-de-sac")
    if turning_loops:
        types.append("turning loop")
    if dead_ends:
        types.append("dead end")

    print("❌ HIGH")
    return CriterionResult(
        criterion="uturn",
        passed=False,
        importance=Importance.HIGH,
        notes=f"Bus would require U-turn or backing — {', '.join(types)} detected within 300ft;",
    )

def check_bike_lane(elements: list) -> CriterionResult:
    """Stop should not have a bike lane students must cross to board."""
    bike_lanes = [
        e for e in elements
        if e.get("type") == "way" and (
            e.get("tags", {}).get("highway") == "cycleway"
            or e.get("tags", {}).get("cycleway") in ("lane", "track")
            or e.get("tags", {}).get("cycleway:right") == "lane"
            or e.get("tags", {}).get("cycleway:left") == "lane"
        )
    ]

    if not bike_lanes:
        return CriterionResult(
            criterion="bike_lane",
            passed=True,
            notes="No bike lane detected near stop;",
        )

    print("❌ HIGH")
    return CriterionResult(
        criterion="bike_lane",
        passed=False,
        importance=Importance.HIGH,
        notes=f"Bike lane detected at stop — students may need to cross to board ({len(bike_lanes)} way(s));",
    )
