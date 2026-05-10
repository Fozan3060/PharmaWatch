"""Lazy Firestore client.

The Firestore connection is created on first use, not at import time, so the
app can boot without Firebase credentials present (useful for local schema
work, scraper runs, and tests with a fake client).

Tests inject a fake via set_firestore_for_testing().
"""

from __future__ import annotations

from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import get_settings

_db: Any | None = None


def get_firestore() -> Any:
    global _db
    if _db is not None:
        return _db
    settings = get_settings()
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
    _db = firestore.client()
    return _db


def set_firestore_for_testing(fake: Any) -> None:
    """Tests use this to substitute a fake client without touching real Firebase."""
    global _db
    _db = fake


def reset_firestore() -> None:
    global _db
    _db = None
