from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_medicines_search_prefix_ranks_first():
    res = client.get("/medicines/search", params={"q": "Cef", "limit": 5})
    assert res.status_code == 200
    rows = res.json()["results"]
    assert any(r["brand_name"] == "Ceftum" for r in rows)
    # Brand-prefix matches must come before substring/generic matches
    first = rows[0]["brand_name"].lower()
    assert first.startswith("cef")


def test_medicines_search_finds_by_active_ingredient():
    res = client.get("/medicines/search", params={"q": "Paracetamol"})
    rows = res.json()["results"]
    brands = {r["brand_name"] for r in rows}
    assert "Panadol" in brands


def test_medicines_search_validates_min_length():
    res = client.get("/medicines/search", params={"q": ""})
    assert res.status_code == 422


def test_pharmacies_known_finds_seeded_pharmacy():
    res = client.get("/pharmacies/known", params={"q": "City Pharmacy"})
    assert res.status_code == 200
    rows = res.json()["results"]
    assert any(r["pharmacy_name"] == "City Pharmacy" and r["city"] == "Karachi" for r in rows)
    target = next(r for r in rows if r["pharmacy_name"] == "City Pharmacy")
    assert target["violation_count"] == 3   # seeded with 3 prior violations
    assert target["area"] == "Saddar"


def test_pharmacies_known_filtered_by_city():
    res = client.get("/pharmacies/known", params={"q": "Pharmacy", "city": "Lahore"})
    rows = res.json()["results"]
    for r in rows:
        assert r["city"] == "Lahore"


def test_pharmacies_known_returns_empty_for_unknown_pharmacy():
    res = client.get("/pharmacies/known", params={"q": "ZzzNotARealPharmacy"})
    assert res.status_code == 200
    assert res.json()["results"] == []


def test_pharmacies_known_finds_curated_chain_with_no_violations():
    """Dvago is a major Pakistani chain with no DRAP enforcement on file —
    must still appear in suggestions, marked with violation_count = 0."""
    res = client.get("/pharmacies/known", params={"q": "Dvago"})
    rows = res.json()["results"]
    assert len(rows) >= 1
    assert all(r["pharmacy_name"] == "Dvago" for r in rows)
    assert all(r["violation_count"] == 0 for r in rows)
    cities = {r["city"] for r in rows}
    assert "Karachi" in cities
