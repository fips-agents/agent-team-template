"""Trust and scrutiny profile derivation."""

from typing import Any


SCRUTINY_CONFIG = {
    "high": {
        "trace_fidelity": "full",
        "question_tool": True,
        "permission_granularity": "granular",
    },
    "medium": {
        "trace_fidelity": "standard",
        "question_tool": False,
        "permission_granularity": "moderate",
    },
    "low": {
        "trace_fidelity": "minimal",
        "question_tool": False,
        "permission_granularity": "broad",
    },
}

SENSITIVITY_TRUST = {
    "restricted": "low",
    "confidential": "low",
    "internal": "medium",
    "public": "high",
}

ACTION_SCOPE_TRUST = {
    "external-calls": "low",
    "delete": "low",
    "write": "medium",
    "read-only": "high",
}

REVERSIBILITY_IMPACT_SCRUTINY = {
    ("low", "high"): "high",
    ("low", "medium"): "medium",
    ("low", "low"): "medium",
    ("medium", "high"): "high",
    ("medium", "medium"): "medium",
    ("medium", "low"): "low",
    ("high", "high"): "medium",
    ("high", "medium"): "low",
    ("high", "low"): "low",
}


def derive_trust_level(fm: dict[str, Any]) -> str:
    """Derive trust level from data sensitivity and action scope.

    Uses the explicit trust_level if set, otherwise derives from
    the most sensitive data source and the broadest action scope.
    """
    if fm.get("trust_level"):
        return fm["trust_level"]

    worst_sensitivity = "public"
    for da in fm.get("data_access", []):
        s = da.get("sensitivity", "public")
        if SENSITIVITY_TRUST.get(s, "high") < SENSITIVITY_TRUST.get(worst_sensitivity, "high"):
            worst_sensitivity = s

    data_trust = SENSITIVITY_TRUST.get(worst_sensitivity, "medium")
    action_trust = ACTION_SCOPE_TRUST.get(fm.get("action_scope", "read-only"), "medium")

    trust_order = ["low", "medium", "high"]
    return min(data_trust, action_trust, key=lambda t: trust_order.index(t))


def derive_scrutiny_level(fm: dict[str, Any]) -> str:
    """Derive scrutiny from reversibility and impact.

    Uses the explicit scrutiny_level if set, otherwise derives from
    reversibility and impact dimensions.
    """
    if fm.get("scrutiny_level"):
        return fm["scrutiny_level"]

    reversibility = fm.get("reversibility", "medium")
    impact = fm.get("impact", "medium")
    return REVERSIBILITY_IMPACT_SCRUTINY.get((reversibility, impact), "medium")
