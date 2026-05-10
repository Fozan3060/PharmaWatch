from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_submit_report_happy_path():
    res = client.post(
        "/reports/submit",
        json={
            "pharmacy_name": "City Pharmacy",
            "pharmacy_area": "Saddar",
            "pharmacy_city": "Karachi",
            "medicine": "Ceftum 500mg",
            "official_mrp_pkr": 640,
            "charged_price_pkr": 1200,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["pharmacy_id"] == "city-pharmacy-saddar-karachi"
    assert body["pharmacy_total_reports_30d"] == 1
    assert body["classification"] == "watch"
    assert body["report_id"]


def test_submit_rejects_when_charged_not_over_mrp():
    res = client.post(
        "/reports/submit",
        json={
            "pharmacy_name": "Test Pharmacy",
            "pharmacy_city": "Karachi",
            "medicine": "Panadol",
            "official_mrp_pkr": 30,
            "charged_price_pkr": 30,  # equal -> not an overcharge
        },
    )
    assert res.status_code == 400
    assert "greater than" in res.json()["detail"]


def test_submit_rejects_invalid_payload():
    res = client.post(
        "/reports/submit",
        json={
            "pharmacy_name": "X",  # min_length 2 -> rejected
            "pharmacy_city": "Karachi",
            "medicine": "Panadol",
            "official_mrp_pkr": 30,
            "charged_price_pkr": 80,
        },
    )
    assert res.status_code == 422


def test_classification_progresses_with_more_submissions():
    base = {
        "pharmacy_name": "Threshold Pharmacy",
        "pharmacy_area": "Test",
        "pharmacy_city": "Karachi",
        "medicine": "Brufen 400mg",
        "official_mrp_pkr": 80,
        "charged_price_pkr": 200,
    }
    classifications = []
    for _ in range(11):
        res = client.post("/reports/submit", json=base)
        assert res.status_code == 200
        classifications.append(res.json()["classification"])
    # 1->watch, 4->suspicious, 10->confirmed (per pattern_detection.classify)
    assert classifications[0] == "watch"
    assert classifications[3] == "suspicious"
    assert classifications[-1] == "confirmed"
