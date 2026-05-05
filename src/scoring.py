from src.models import CriterionResult, Importance

IMPORTANCE_WEIGHTS = {
    Importance.CRITICAL: 40,
    Importance.HIGH:     20,
    Importance.MEDIUM:   10,
    Importance.LOW:       5,
}

def compute_score(results: list[CriterionResult]) -> dict:
    """
    Returns a score 0-100, a verdict, and failures grouped by importance.
    Any single CRITICAL failure → INADEQUATE regardless of score.
    """
    total_weight = 0
    lost_weight = 0

    failures = {
        "critical": [],
        "high":     [],
        "medium":   [],
        "low":      [],
    }

    for r in results:
        if r.passed is None or r.importance is None:
            continue
        weight = IMPORTANCE_WEIGHTS.get(r.importance, 0)
        total_weight += weight
        if not r.passed:
            lost_weight += weight
            failures[r.importance.value].append({
                "criterion": r.criterion,
                "notes": r.notes,
            })

    score = round((1 - lost_weight / total_weight) * 100, 1) if total_weight > 0 else None

    if failures["critical"]:
        verdict = "INADEQUATE"
    elif score is None:
        verdict = "UNKNOWN"
    elif score >= 75:
        verdict = "ADEQUATE"
    elif score >= 50:
        verdict = "REVIEW"
    else:
        verdict = "INADEQUATE"

    return {
        "score": score,
        "verdict": verdict,
        "failures": failures,
    }
