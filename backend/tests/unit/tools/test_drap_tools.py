from app.agent.tools import all_tools, dispatch


def test_all_four_drap_tools_registered():
    names = {t.name for t in all_tools()}
    assert {
        "drap_price_lookup",
        "generic_alternatives",
        "spurious_alert_check",
        "drap_enforcement_lookup",
    }.issubset(names)


async def test_price_lookup_exact_match():
    result = await dispatch("drap_price_lookup", medicine_name="Ceftum", strength="500mg")
    assert result["found"] is True
    assert result["mrp_pkr"] == 640
    assert result["active_ingredient"] == "Cefuroxime"


async def test_price_lookup_case_insensitive():
    result = await dispatch("drap_price_lookup", medicine_name="ceftum")
    assert result["found"] is True


async def test_price_lookup_partial_returns_did_you_mean():
    # 'Ceftu' is not an exact brand but is a substring of 'Ceftum'
    result = await dispatch("drap_price_lookup", medicine_name="Ceftu")
    assert result["found"] is False
    assert result["reason"] == "no_exact_match"
    assert any(c["brand_name"] == "Ceftum" for c in result["did_you_mean"])


async def test_price_lookup_truly_unknown():
    result = await dispatch("drap_price_lookup", medicine_name="ZzzNotARealMedicine")
    assert result["found"] is False
    assert result["reason"] == "not_in_drap_database"


async def test_generic_alternatives_returns_cheapest_first():
    result = await dispatch("generic_alternatives", active_ingredient="Cefuroxime", strength="500mg")
    assert result["count"] >= 3
    prices = [a["mrp_pkr"] for a in result["alternatives"]]
    assert prices == sorted(prices)
    assert prices[0] == 390  # Cefim by Hilton


async def test_spurious_alert_hit():
    result = await dispatch("spurious_alert_check", medicine_name="Augmentin", batch_number="AB-2024-1284")
    assert result["alert"] is True
    assert result["alerts"][0]["reason"] == "counterfeit"


async def test_spurious_alert_miss():
    result = await dispatch("spurious_alert_check", medicine_name="Panadol")
    assert result["alert"] is False
    assert result["count"] == 0


async def test_enforcement_lookup_demo_pharmacy():
    """City Pharmacy / Saddar / Karachi should have 3 prior violations including a critical one."""
    result = await dispatch("drap_enforcement_lookup",
                            pharmacy_name="City Pharmacy", city="Karachi", area="Saddar")
    assert result["found"] is True
    assert result["violation_count"] == 3
    assert result["summary"]["total_fines_pkr"] == 250000
    assert result["summary"]["severity_breakdown"].get("critical") == 1
    notice_refs = [v["drap_notice_ref"] for v in result["violations"]]
    assert "DRAP/ENF/2024/1284" in notice_refs


async def test_enforcement_lookup_unknown_pharmacy():
    result = await dispatch("drap_enforcement_lookup",
                            pharmacy_name="Nonexistent Pharmacy", city="Karachi")
    assert result["found"] is False
