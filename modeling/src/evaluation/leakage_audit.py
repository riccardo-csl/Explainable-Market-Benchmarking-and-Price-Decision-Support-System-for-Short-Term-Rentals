"""Leakage audit rules for Goal 2 feature sets."""

from __future__ import annotations


FORBIDDEN_TRAINING_SUBSTRINGS = [
    "nightly_price_median",
    "nightly_price_median_abs_deviation",
    "price_median",
    "price_positioning",
]


def audit_feature_columns(feature_columns: list[str]) -> list[str]:
    """Return leakage findings for a candidate feature set."""

    findings: list[str] = []
    for column in feature_columns:
        lower_column = column.lower()
        for forbidden_substring in FORBIDDEN_TRAINING_SUBSTRINGS:
            if forbidden_substring in lower_column:
                findings.append(
                    f"Feature `{column}` contains forbidden substring `{forbidden_substring}`."
                )
                break
    return findings
