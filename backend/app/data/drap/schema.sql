-- PharmaWatch DRAP Local "Golden Source" schema
-- Built from publicly-scraped DRAP data. No live drap.gov.pk dependency at runtime.
--
-- Apply with: sqlite3 data_store/drap.sqlite < app/data/drap/schema.sql

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ─────────────────────────────────────────────────────────────────────
-- medicines: registered medicines with official MRP
-- Source: drap.gov.pk/medicine-prices + drap.gov.pk/registered-products
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medicines (
    reg_number          TEXT PRIMARY KEY,
    brand_name          TEXT NOT NULL,
    generic_name        TEXT,
    active_ingredient   TEXT NOT NULL,
    strength            TEXT NOT NULL,
    dosage_form         TEXT,                -- tablet, syrup, injection, etc.
    pack_size           TEXT,
    mrp_pkr             INTEGER NOT NULL,
    manufacturer        TEXT,
    last_updated        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_med_brand
    ON medicines(brand_name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_med_ingredient
    ON medicines(active_ingredient COLLATE NOCASE, strength);
CREATE INDEX IF NOT EXISTS idx_med_generic
    ON medicines(generic_name COLLATE NOCASE);


-- ─────────────────────────────────────────────────────────────────────
-- spurious_alerts: counterfeit/substandard medicine warnings from DRAP
-- Source: drap.gov.pk/spurious-medicines + drap.gov.pk/enforcement
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS spurious_alerts (
    alert_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name       TEXT NOT NULL,
    batch_number        TEXT,
    manufacturer        TEXT,
    reason              TEXT NOT NULL,       -- 'counterfeit' | 'substandard' | 'mislabeled' | 'unregistered'
    alert_date          DATE NOT NULL,
    drap_notice_ref     TEXT NOT NULL,
    source_url          TEXT,
    is_active           BOOLEAN NOT NULL DEFAULT 1,
    scraped_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_spurious_med
    ON spurious_alerts(medicine_name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_spurious_batch
    ON spurious_alerts(batch_number);


-- ─────────────────────────────────────────────────────────────────────
-- local_drap_enforcement: pharmacy-level enforcement history
-- THE killer table — the "Undeniable Investigation Report" data source.
-- Source: drap.gov.pk/enforcement + manual curation from news archives
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS local_drap_enforcement (
    -- Identity
    violation_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id         TEXT NOT NULL,       -- normalized slug, e.g. "city-pharmacy-saddar-karachi"
    pharmacy_name       TEXT NOT NULL,       -- display name as published
    pharmacy_license_no TEXT,                -- DRAP license # if available
    city                TEXT NOT NULL,
    area                TEXT,
    address             TEXT,

    -- Violation core
    violation_type      TEXT NOT NULL,       -- 'overcharging' | 'counterfeit_sale' | 'expired_stock'
                                             -- | 'unlicensed_operation' | 'spurious_medicine'
                                             -- | 'narcotic_violation' | 'illegal_import' | 'storage_violation'
    violation_date      DATE NOT NULL,
    medicine_involved   TEXT,                -- nullable — not all violations are medicine-specific
    description         TEXT NOT NULL,       -- human-readable narrative from the notice

    -- Penalty (the "undeniable" part)
    penalty_type        TEXT,                -- 'fine' | 'license_suspended' | 'license_cancelled'
                                             -- | 'warning' | 'stock_seized' | 'criminal_referral'
    penalty_amount_pkr  INTEGER,
    suspension_days     INTEGER,

    -- Evidence chain
    drap_notice_ref     TEXT,                -- e.g. "DRAP/ENF/2024/1284"
    source_url          TEXT NOT NULL,       -- direct link to drap.gov.pk notice OR news article
    source_type         TEXT NOT NULL,       -- 'drap_official' | 'news_dawn' | 'news_geo' | 'news_tribune'
    issuing_authority   TEXT,                -- 'DRAP' | 'Provincial Health Dept' | 'Police'

    -- Computed / metadata
    severity            TEXT NOT NULL,       -- 'low' | 'medium' | 'high' | 'critical'
    is_resolved         BOOLEAN NOT NULL DEFAULT 0,
    scraped_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_verified_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_enf_pharmacy_id
    ON local_drap_enforcement(pharmacy_id);
CREATE INDEX IF NOT EXISTS idx_enf_pharmacy_city
    ON local_drap_enforcement(pharmacy_name COLLATE NOCASE, city COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_enf_violation_date
    ON local_drap_enforcement(violation_date DESC);
CREATE INDEX IF NOT EXISTS idx_enf_severity
    ON local_drap_enforcement(severity);


-- ─────────────────────────────────────────────────────────────────────
-- scrape_metadata: track when each table was last refreshed
-- Surfaced in the UI as "Data current as of YYYY-MM-DD"
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scrape_metadata (
    table_name          TEXT PRIMARY KEY,
    last_scraped_at     TIMESTAMP NOT NULL,
    row_count           INTEGER NOT NULL,
    source_url          TEXT
);
