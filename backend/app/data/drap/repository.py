"""SQLite query helpers for the DRAP local Golden Source.

All queries are inline and explicit — no ORM. Each function returns a list of
plain dicts (or a single dict / None) so tools can pass them to Gemini directly.
"""

from __future__ import annotations

from typing import Any

from app.data.drap.client import get_connection


def find_medicine_by_brand(brand_name: str, strength: str | None = None) -> dict[str, Any] | None:
    """Exact case-insensitive lookup by brand name (+ optional strength)."""
    with get_connection() as conn:
        if strength:
            row = conn.execute(
                """
                SELECT * FROM medicines
                WHERE LOWER(brand_name) = LOWER(?)
                  AND LOWER(REPLACE(strength, ' ', '')) = LOWER(REPLACE(?, ' ', ''))
                LIMIT 1
                """,
                (brand_name, strength),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM medicines WHERE LOWER(brand_name) = LOWER(?) LIMIT 1",
                (brand_name,),
            ).fetchone()
        return dict(row) if row else None


def search_medicines_like(needle: str, limit: int = 5) -> list[dict[str, Any]]:
    """Substring match on brand or generic name. Used for retry / fuzzy fallback."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM medicines
            WHERE brand_name   LIKE '%' || ? || '%' COLLATE NOCASE
               OR generic_name LIKE '%' || ? || '%' COLLATE NOCASE
            ORDER BY mrp_pkr ASC
            LIMIT ?
            """,
            (needle, needle, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def find_generics_by_ingredient(
    active_ingredient: str,
    strength: str | None = None,
    exclude_reg_number: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """All medicines sharing the active ingredient (and strength if given), sorted cheapest first."""
    sql = """
        SELECT * FROM medicines
        WHERE LOWER(active_ingredient) = LOWER(?)
    """
    params: list[Any] = [active_ingredient]
    if strength:
        sql += " AND LOWER(REPLACE(strength, ' ', '')) = LOWER(REPLACE(?, ' ', ''))"
        params.append(strength)
    if exclude_reg_number:
        sql += " AND reg_number != ?"
        params.append(exclude_reg_number)
    sql += " ORDER BY mrp_pkr ASC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def find_spurious_alerts(medicine_name: str, batch_number: str | None = None) -> list[dict[str, Any]]:
    sql = """
        SELECT * FROM spurious_alerts
        WHERE LOWER(medicine_name) LIKE '%' || LOWER(?) || '%'
          AND is_active = 1
    """
    params: list[Any] = [medicine_name]
    if batch_number:
        sql += " AND batch_number = ?"
        params.append(batch_number)
    sql += " ORDER BY alert_date DESC"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def find_enforcement_by_pharmacy(
    pharmacy_id: str | None = None,
    pharmacy_name: str | None = None,
    city: str | None = None,
) -> list[dict[str, Any]]:
    """Lookup enforcement history by slug (preferred) or by name+city fallback."""
    if pharmacy_id:
        sql = "SELECT * FROM local_drap_enforcement WHERE pharmacy_id = ? ORDER BY violation_date DESC"
        params: list[Any] = [pharmacy_id]
    else:
        if not pharmacy_name:
            return []
        sql = """
            SELECT * FROM local_drap_enforcement
            WHERE LOWER(pharmacy_name) LIKE '%' || LOWER(?) || '%'
        """
        params = [pharmacy_name]
        if city:
            sql += " AND LOWER(city) = LOWER(?)"
            params.append(city)
        sql += " ORDER BY violation_date DESC"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
