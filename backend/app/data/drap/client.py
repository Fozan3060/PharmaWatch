import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.config import get_settings

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(db_path: Path | None = None) -> None:
    """Idempotent — safe to call on app start or from scripts."""
    db_path = db_path or get_settings().drap_sqlite_abspath
    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = _SCHEMA_PATH.read_text()
    with _connect(db_path) as conn:
        conn.executescript(schema_sql)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    db_path = get_settings().drap_sqlite_abspath
    if not db_path.exists():
        init_schema(db_path)
    conn = _connect(db_path)
    try:
        yield conn
    finally:
        conn.close()
