"""Quality scoring engine computing sub-scores, weights, aggregate score, and quality label."""
from typing import List, Dict, Any, Tuple

# Sub-score weights (Total: 1.0)
WEIGHT_UNAMBIGUOUS = 0.30
WEIGHT_VERIFIABLE = 0.30
WEIGHT_COMPLETE = 0.20
WEIGHT_ATOMIC = 0.20

SEVERITY_PENALTIES = {
    "CRITICAL": 35.0,
    "HIGH": 25.0,
    "MEDIUM": 15.0,
    "LOW": 10.0,
}


def calculate_quality_score(issues: List[Dict[str, Any]]) -> Tuple[float, str, Dict[str, float]]:
    """Compute sub-scores, overall quality score (0-100), and quality status label."""
    sub_scores = {
        "unambiguous": 100.0,
        "verifiable": 100.0,
        "complete": 100.0,
        "atomic": 100.0,
    }

    for issue in issues:
        category = issue.get("category", "").upper()
        severity = issue.get("severity", "MEDIUM").upper()
        penalty = SEVERITY_PENALTIES.get(severity, 15.0)

        if category in ("AMBIGUITY", "VAGUENESS", "PASSIVE_VOICE"):
            sub_scores["unambiguous"] = max(0.0, sub_scores["unambiguous"] - penalty)
        elif category == "NON_TESTABILITY":
            sub_scores["verifiable"] = max(0.0, sub_scores["verifiable"] - penalty)
        elif category == "INCOMPLETENESS":
            sub_scores["complete"] = max(0.0, sub_scores["complete"] - penalty)
        elif category == "NON_ATOMIC":
            sub_scores["atomic"] = max(0.0, sub_scores["atomic"] - penalty)
        else:
            sub_scores["unambiguous"] = max(0.0, sub_scores["unambiguous"] - penalty)

    aggregate_score = round(
        (sub_scores["unambiguous"] * WEIGHT_UNAMBIGUOUS)
        + (sub_scores["verifiable"] * WEIGHT_VERIFIABLE)
        + (sub_scores["complete"] * WEIGHT_COMPLETE)
        + (sub_scores["atomic"] * WEIGHT_ATOMIC),
        1,
    )

    if aggregate_score >= 80.0:
        quality_label = "GOOD"
    elif aggregate_score >= 50.0:
        quality_label = "NEEDS_IMPROVEMENT"
    else:
        quality_label = "POOR"

    return aggregate_score, quality_label, sub_scores
