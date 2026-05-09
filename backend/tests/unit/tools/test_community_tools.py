from app.agent.tools import all_tools, dispatch


def test_community_tools_registered():
    names = {t.name for t in all_tools()}
    assert {"log_community_report", "get_pharmacy_reports"}.issubset(names)


async def test_log_report_writes_and_returns_count():
    result = await dispatch(
        "log_community_report",
        pharmacy_name="City Pharmacy",
        area="Saddar",
        city="Karachi",
        medicine="Ceftum 500mg",
        official_mrp=640,
        charged_price=1200,
    )
    assert result["logged"] is True
    assert result["pharmacy_id"] == "city-pharmacy-saddar-karachi"
    assert result["pharmacy_total_reports_30d"] == 1
    assert result["classification"] == "watch"


async def test_classification_progression():
    """1-3 = watch, 4-9 = suspicious, 10+ = confirmed."""
    base = {"pharmacy_name": "Test Pharmacy", "area": "DHA", "city": "Karachi",
                "medicine": "Brufen 400mg", "official_mrp": 80, "charged_price": 240}

    for i in range(1, 11):
        result = await dispatch("log_community_report", **base)
        if i <= 3:
            assert result["classification"] == "watch", f"i={i}"
        elif i <= 9:
            assert result["classification"] == "suspicious", f"i={i}"
        else:
            assert result["classification"] == "confirmed", f"i={i}"


async def test_get_reports_aggregates_correctly():
    base = {"pharmacy_name": "Sehat Pharmacy", "area": "Gulshan", "city": "Karachi"}
    await dispatch("log_community_report", **base, medicine="Ceftum 500mg",
                   official_mrp=640, charged_price=1200)
    await dispatch("log_community_report", **base, medicine="Augmentin 625mg",
                   official_mrp=1200, charged_price=2000)

    result = await dispatch("get_pharmacy_reports",
                            pharmacy_name="Sehat Pharmacy", area="Gulshan", city="Karachi")
    assert result["pharmacy_id"] == "sehat-pharmacy-gulshan-karachi"
    assert result["report_count"] == 2
    assert result["classification"] == "watch"
    assert set(result["medicines_flagged"]) == {"Ceftum 500mg", "Augmentin 625mg"}
    # Overcharge: (1200-640)/640 * 100 = 87.5%, (2000-1200)/1200 * 100 = 66.7% -> avg ~77.1
    assert 75 <= result["avg_overcharge_pct"] <= 80


async def test_get_reports_for_unknown_pharmacy():
    result = await dispatch("get_pharmacy_reports",
                            pharmacy_name="Nonexistent", city="Karachi")
    assert result["report_count"] == 0
    assert result["classification"] == "clean"
