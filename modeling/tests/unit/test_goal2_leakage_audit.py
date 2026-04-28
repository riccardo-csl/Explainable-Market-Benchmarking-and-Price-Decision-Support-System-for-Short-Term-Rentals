from evaluation.leakage_audit import audit_feature_columns


def test_audit_feature_columns_flags_price_proxy_columns() -> None:
    findings = audit_feature_columns(
        ["room_type", "nightly_price_median_context", "distance_to_city_center_km"]
    )

    assert len(findings) == 1
    assert "nightly_price_median_context" in findings[0]


def test_audit_feature_columns_accepts_goal2_feature_set() -> None:
    findings = audit_feature_columns(["room_type", "distance_to_city_center_km"])

    assert findings == []
