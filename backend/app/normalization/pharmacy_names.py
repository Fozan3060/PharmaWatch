"""Pharmacy name normalization.

The same physical pharmacy may be reported as "City Pharmacy", "city pharmacy",
or "CITY PHARMACY SADDAR". We canonicalize to a slug for joins:
  ("City Pharmacy", "Saddar", "Karachi") -> "city-pharmacy-saddar-karachi"
"""

from __future__ import annotations

from slugify import slugify


def make_pharmacy_id(name: str, area: str | None, city: str) -> str:
    parts = [name, area, city]
    return slugify(" ".join(p for p in parts if p))
