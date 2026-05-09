"""Normalize medicine name input — lowercase, strip punctuation, collapse spaces.

The agent receives free-text user input ("Augmentin 625", "augmentin", "AUGMENTIN-625").
Tools call normalize() before SQL lookup so all variants hit the same row.
"""

from __future__ import annotations

import re

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")


def normalize(name: str) -> str:
    if not name:
        return ""
    s = _PUNCT.sub(" ", name.lower())
    return _WS.sub(" ", s).strip()


def normalize_strength(strength: str | None) -> str | None:
    if not strength:
        return None
    s = strength.lower().replace(" ", "")
    # Standardize common suffixes: "500 mg" / "500mgs" / "500MG" -> "500mg"
    s = re.sub(r"(\d+)\s*mgs?", r"\1mg", s)
    s = re.sub(r"(\d+)\s*mls?", r"\1ml", s)
    return s
