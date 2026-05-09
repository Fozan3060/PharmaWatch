"""Seed the local SQLite Golden Source from JSON fixtures.

Loads ./data_store/seed/{medicines,spurious_alerts,enforcement}.json into the
SQLite DB. Idempotent — safe to re-run; existing rows are upserted by
natural key.

This is the demo / development entrypoint. Production refresh is done by
scripts/scrape_drap.py against drap.gov.pk.

Run:
    python scripts/seed_drap.py
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.drap.client import get_connection, init_schema  # noqa: E402
from app.normalization.pharmacy_names import make_pharmacy_id  # noqa: E402

log = logging.getLogger("seed_drap")

SEED_DIR = Path(__file__).resolve().parents[1] / "data_store" / "seed"


def _load(name: str) -> list[dict]:
    return json.loads((SEED_DIR / name).read_text())


def seed_medicines() -> int:
    rows = _load("medicines.json")
    now = datetime.now(UTC).isoformat()
    for r in rows:
        r["last_updated"] = now
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO medicines (reg_number, brand_name, generic_name, active_ingredient,
                                   strength, dosage_form, pack_size, mrp_pkr, manufacturer, last_updated)
            VALUES (:reg_number, :brand_name, :generic_name, :active_ingredient,
                    :strength, :dosage_form, :pack_size, :mrp_pkr, :manufacturer, :last_updated)
            ON CONFLICT(reg_number) DO UPDATE SET
                brand_name=excluded.brand_name, generic_name=excluded.generic_name,
                active_ingredient=excluded.active_ingredient, strength=excluded.strength,
                dosage_form=excluded.dosage_form, pack_size=excluded.pack_size,
                mrp_pkr=excluded.mrp_pkr, manufacturer=excluded.manufacturer,
                last_updated=excluded.last_updated
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def seed_spurious_alerts() -> int:
    rows = _load("spurious_alerts.json")
    with get_connection() as conn:
        # Wipe + insert: spurious alerts have no stable natural key in our schema.
        conn.execute("DELETE FROM spurious_alerts")
        conn.executemany(
            """
            INSERT INTO spurious_alerts (medicine_name, batch_number, manufacturer, reason,
                                          alert_date, drap_notice_ref, source_url)
            VALUES (:medicine_name, :batch_number, :manufacturer, :reason,
                    :alert_date, :drap_notice_ref, :source_url)
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def seed_enforcement() -> int:
    rows = _load("enforcement.json")
    for r in rows:
        r["pharmacy_id"] = make_pharmacy_id(r["pharmacy_name"], r.get("area"), r["city"])
    with get_connection() as conn:
        conn.execute("DELETE FROM local_drap_enforcement")
        conn.executemany(
            """
            INSERT INTO local_drap_enforcement (
                pharmacy_id, pharmacy_name, pharmacy_license_no, city, area, address,
                violation_type, violation_date, medicine_involved, description,
                penalty_type, penalty_amount_pkr, suspension_days,
                drap_notice_ref, source_url, source_type, issuing_authority,
                severity, is_resolved
            )
            VALUES (
                :pharmacy_id, :pharmacy_name, :pharmacy_license_no, :city, :area, :address,
                :violation_type, :violation_date, :medicine_involved, :description,
                :penalty_type, :penalty_amount_pkr, :suspension_days,
                :drap_notice_ref, :source_url, :source_type, :issuing_authority,
                :severity, :is_resolved
            )
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def record_scrape(table_name: str, row_count: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scrape_metadata (table_name, last_scraped_at, row_count, source_url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(table_name) DO UPDATE SET
                last_scraped_at=excluded.last_scraped_at,
                row_count=excluded.row_count
            """,
            (table_name, datetime.now(UTC).isoformat(), row_count, "seed:local-fixtures"),
        )
        conn.commit()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    init_schema()

    n_med = seed_medicines()
    record_scrape("medicines", n_med)
    log.info("medicines: %d rows", n_med)

    n_alert = seed_spurious_alerts()
    record_scrape("spurious_alerts", n_alert)
    log.info("spurious_alerts: %d rows", n_alert)

    n_enf = seed_enforcement()
    record_scrape("local_drap_enforcement", n_enf)
    log.info("local_drap_enforcement: %d rows", n_enf)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
