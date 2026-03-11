"""Normalization utilities for cleaned datasets."""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

import pandas as pd


_KNOWN_TEXT_ALIASES = {
    "PARCO BOSCO IN CITT\x85": "PARCO BOSCO IN CITTÀ",
    "PARCO BOSCO IN CITTÂ…": "PARCO BOSCO IN CITTÀ",
    "PARCO BOSCO IN CITTÂ...": "PARCO BOSCO IN CITTÀ",
    "VII San Giovanni/CinecittÃ\xa0": "VII San Giovanni/Cinecittà",
    "VII San Giovanni/CinecittÃ": "VII San Giovanni/Cinecittà",
}

_CITY_LABELS = {
    "firenze": "Firenze",
    "milano": "Milano",
    "napoli": "Napoli",
    "roma": "Roma",
    "venezia": "Venezia",
}

_PERIOD_LABELS = {
    "early spring": "Early Spring",
    "early summer": "Early Summer",
    "early autumn": "Early Autumn",
    "early winter": "Early Winter",
}


def normalize_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).replace("\ufeff", "").strip(" \t\r\n")
    if not text:
        return None

    if text in _KNOWN_TEXT_ALIASES:
        text = _KNOWN_TEXT_ALIASES[text]
    elif any(marker in text for marker in ("Ã", "Â")):
        for encoding in ("cp1252", "latin1"):
            try:
                repaired = text.encode(encoding).decode("utf-8")
            except Exception:
                continue
            if repaired in _KNOWN_TEXT_ALIASES:
                text = _KNOWN_TEXT_ALIASES[repaired]
                break
            if all(marker not in repaired for marker in ("Ã", "Â")):
                text = repaired
                break

    text = unicodedata.normalize("NFKC", text)
    text = " ".join(text.split())
    return _KNOWN_TEXT_ALIASES.get(text, text)


def normalize_city_label(value: Any) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None
    return _CITY_LABELS.get(text.casefold(), text)


def normalize_period_label(value: Any) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None
    return _PERIOD_LABELS.get(text.casefold(), text)


def normalize_superhost_flag(value: Any) -> bool | None:
    text = normalize_text(value)
    if text is None:
        return None
    mapping = {
        "superhost": True,
        "host": False,
    }
    return mapping.get(text.casefold())


def parse_coordinates(value: Any) -> tuple[float | None, float | None]:
    text = normalize_text(value)
    if text is None:
        return (None, None)

    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 2:
        return (None, None)

    try:
        latitude = float(parts[0])
        longitude = float(parts[1])
    except ValueError:
        return (None, None)

    return (latitude, longitude)


def slugify_text(value: Any) -> str:
    text = normalize_text(value) or "unknown"
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.casefold()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    return ascii_text or "unknown"


def geometry_to_json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
