"""DRAP scraper — one-shot CLI to populate the local SQLite Golden Source.

Run before the hackathon to seed:
  - medicines
  - spurious_alerts

For deployment as a nightly cron:
  0 2 * * *  /usr/bin/python /app/backend/scripts/scrape_drap.py

Sources (per SRS Appendix A):
  - drap.gov.pk/medicine-prices
  - drap.gov.pk/registered-products
  - drap.gov.pk/spurious-medicines

NOTE: Implementation pending. Skeleton only — actual HTML parsing depends on
the live site structure and is subject to change. See Day 1 morning of PROJECT_PLAN.md.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

# Make the app package importable when running as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.drap.client import get_connection, init_schema  # noqa: E402

log = logging.getLogger("scrape_drap")


def scrape_medicines() -> list[dict]:
    """TODO(day 1): hit drap.gov.pk/medicine-prices, parse table rows."""
    log.warning("scrape_medicines: not yet implemented")
    return []


def scrape_spurious_alerts() -> list[dict]:
    """TODO(day 1): hit drap.gov.pk/spurious-medicines, parse alerts."""
    log.warning("scrape_spurious_alerts: not yet implemented")
    return []


def upsert_medicines(rows: list[dict]) -> int:
    if not rows:
        return 0
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO medicines (
                reg_number, brand_name, generic_name, active_ingredient,
                strength, dosage_form, pack_size, mrp_pkr, manufacturer, last_updated
            )
            VALUES (
                :reg_number, :brand_name, :generic_name, :active_ingredient,
                :strength, :dosage_form, :pack_size, :mrp_pkr, :manufacturer, :last_updated
            )
            ON CONFLICT(reg_number) DO UPDATE SET
                brand_name        = excluded.brand_name,
                generic_name      = excluded.generic_name,
                active_ingredient = excluded.active_ingredient,
                strength          = excluded.strength,
                dosage_form       = excluded.dosage_form,
                pack_size         = excluded.pack_size,
                mrp_pkr           = excluded.mrp_pkr,
                manufacturer      = excluded.manufacturer,
                last_updated      = excluded.last_updated
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def record_scrape(table_name: str, row_count: int, source_url: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scrape_metadata (table_name, last_scraped_at, row_count, source_url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(table_name) DO UPDATE SET
                last_scraped_at = excluded.last_scraped_at,
                row_count       = excluded.row_count,
                source_url      = excluded.source_url
            """,
            (table_name, datetime.now(UTC).isoformat(), row_count, source_url),
        )
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape DRAP data into local SQLite.")
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Just create the schema, don't scrape.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    init_schema()
    log.info("Schema initialized at %s", get_connection.__module__)

    if args.init_only:
        return 0

    medicines = scrape_medicines()
    n = upsert_medicines(medicines)
    record_scrape("medicines", n, "https://drap.gov.pk/medicine-prices")
    log.info("medicines: upserted %d rows", n)

    # alerts = scrape_spurious_alerts()
    # n = upsert_spurious_alerts(alerts)
    # record_scrape("spurious_alerts", n, "https://drap.gov.pk/spurious-medicines")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
