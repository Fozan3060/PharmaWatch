"""Shared pytest fixtures: isolated SQLite + in-memory Firestore."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolated_drap_db():
    """Point DRAP_SQLITE_PATH at a temp DB and seed it once for the whole test session."""
    tmpdir = tempfile.mkdtemp(prefix="pharmawatch-test-")
    db_path = Path(tmpdir) / "drap.sqlite"
    os.environ["DRAP_SQLITE_PATH"] = str(db_path)

    from app.config import get_settings
    get_settings.cache_clear()

    from app.data.drap.client import init_schema
    from scripts.seed_drap import seed_enforcement, seed_medicines, seed_spurious_alerts

    init_schema(db_path)
    seed_medicines()
    seed_spurious_alerts()
    seed_enforcement()

    yield db_path


@pytest.fixture(autouse=True)
def fake_firestore():
    """Fresh in-memory Firestore for every test so writes don't bleed between cases."""
    from app.data.firebase.client import reset_firestore, set_firestore_for_testing
    from tests.fakes.firestore import FakeFirestore

    fake = FakeFirestore()
    set_firestore_for_testing(fake)
    yield fake
    reset_firestore()
