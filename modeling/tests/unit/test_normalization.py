from data_foundation.normalization import (
    normalize_city_label,
    normalize_period_label,
    normalize_superhost_flag,
    normalize_text,
    parse_coordinates,
    slugify_text,
)


def test_normalize_text_repairs_known_encoding_issues() -> None:
    assert normalize_text("PARCO BOSCO IN CITT\x85") == "PARCO BOSCO IN CITTÀ"
    assert normalize_text("PARCO BOSCO IN CITTÂ…") == "PARCO BOSCO IN CITTÀ"
    assert normalize_text("VII San Giovanni/CinecittÃ\xa0") == "VII San Giovanni/Cinecittà"


def test_normalize_period_and_city_labels_use_canonical_values() -> None:
    assert normalize_city_label(" roma ") == "Roma"
    assert normalize_period_label("early spring") == "Early Spring"


def test_normalize_superhost_flag_maps_known_values() -> None:
    assert normalize_superhost_flag("Superhost") is True
    assert normalize_superhost_flag("Host") is False
    assert normalize_superhost_flag("Unknown") is None


def test_parse_coordinates_returns_numeric_pair() -> None:
    assert parse_coordinates("43.77709, 11.25216") == (43.77709, 11.25216)
    assert parse_coordinates("bad-value") == (None, None)


def test_slugify_text_produces_stable_slug() -> None:
    assert slugify_text("VII San Giovanni/Cinecittà") == "vii_san_giovanni_cinecitta"
