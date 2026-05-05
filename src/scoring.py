from src.models import CriterionResult, Importance

PENALTY_FACTORS = {
    Importance.CRITICAL: 0.40,
    Importance.HIGH:     0.72,
    Importance.MEDIUM:   0.88,
    Importance.LOW:      0.95,
}

BONUS_PENALTIES = {
    Importance.CRITICAL: 25,
    Importance.HIGH:      0,
    Importance.MEDIUM:    0,
    Importance.LOW:       0,
}

def compute_score(results: list[CriterionResult]) -> dict:
    failures = {"critical": [], "high": [], "medium": [], "low": []}
    score = 100.0
    bonus_deductions = 0

    for r in results:
        if r.passed is None or r.importance is None:
            continue
        if not r.passed:
            score *= PENALTY_FACTORS[r.importance]
            bonus_deductions += BONUS_PENALTIES[r.importance]
            failures[r.importance.value].append({
                "criterion": r.criterion,
                "notes": r.notes,
            })

    score = round(score - bonus_deductions, 1)

    if failures["critical"]:
        verdict = "INADEQUATE"
    elif score is None:
        verdict = "UNKNOWN"
    elif score >= 80:
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
