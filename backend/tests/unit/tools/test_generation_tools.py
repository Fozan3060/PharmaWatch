from app.agent.tools import all_tools, dispatch


def test_generation_tools_registered():
    names = {t.name for t in all_tools()}
    assert {"generate_complaint_letter", "generate_collective_dossier"}.issubset(names)


async def test_complaint_letter_includes_evidence_and_citations():
    result = await dispatch(
        "generate_complaint_letter",
        pharmacy_name="City Pharmacy",
        pharmacy_city="Karachi",
        pharmacy_area="Saddar",
        medicine_name="Ceftum",
        strength="500mg",
        drap_reg_number="DRAP-001-CEF",
        active_ingredient="Cefuroxime",
        manufacturer="GlaxoSmithKline Pakistan",
        official_mrp_pkr=640,
        charged_price_pkr=1200,
        incident_date="2026-05-09",
        prior_violations_summary=(
            "DRAP records show 3 prior enforcement actions: Rs. 250,000 fine for counterfeit "
            "sale (DRAP/ENF/2024/1284), 30-day license suspension (DRAP/ENF/2024/3287), "
            "and a formal warning for cold-chain violation (DRAP/ENF/2025/0142)."
        ),
    )

    assert result["is_anonymous"] is True
    assert result["incident"]["overcharge_amt_pkr"] == 560
    assert result["incident"]["overcharge_pct"] == 87.5
    headings = [s["heading"] for s in result["body_sections"]]
    assert "Pharmacy Enforcement History" in headings
    assert any("DRAP/ENF/2024/1284" in p
               for s in result["body_sections"]
               for p in s.get("paragraphs", []))


async def test_complaint_letter_named_complainant():
    result = await dispatch(
        "generate_complaint_letter",
        pharmacy_name="Sehat Pharmacy",
        pharmacy_city="Karachi",
        medicine_name="Brufen",
        drap_reg_number="DRAP-030-IBU",
        official_mrp_pkr=80,
        charged_price_pkr=240,
        incident_date="2026-05-08",
        complainant_name="Asad Khan",
    )
    assert result["is_anonymous"] is False
    assert result["complainant_name"] == "Asad Khan"


async def test_collective_dossier_aggregates_and_verifies():
    # Seed reports directly via the repo (the agent no longer has a
    # log_community_report tool — submissions go through POST /reports/submit).
    from app.data.firebase import reports_repo
    from app.normalization.pharmacy_names import make_pharmacy_id

    pid = make_pharmacy_id("City Pharmacy", "Saddar", "Karachi")
    base = {"pharmacyId": pid, "pharmacyName": "City Pharmacy",
            "area": "Saddar", "city": "Karachi"}
    reports_repo.add_report({**base, "medicine": "Ceftum", "officialMRP": 640, "chargedPrice": 1200})
    reports_repo.add_report({**base, "medicine": "Augmentin", "officialMRP": 1200, "chargedPrice": 2400})
    reports_repo.add_report({**base, "medicine": "Brufen", "officialMRP": 80, "chargedPrice": 180})
    # One report whose claimed overcharge isn't actually above current MRP -> not verified
    reports_repo.add_report({**base, "medicine": "Ceftum", "officialMRP": 640, "chargedPrice": 600})

    dossier = await dispatch(
        "generate_collective_dossier",
        pharmacy_name="City Pharmacy", pharmacy_city="Karachi", pharmacy_area="Saddar",
    )

    assert dossier["pharmacy"]["id"] == "city-pharmacy-saddar-karachi"
    assert dossier["stats"]["total_reports"] == 4
    assert dossier["stats"]["verified_incidents"] == 3
    assert dossier["stats"]["enforcement_count"] == 3   # pre-seeded enforcement
    assert "Ceftum" in dossier["stats"]["medicines_involved"]
    assert dossier["sections"]["enforcement"]["rows"][0]["drap_notice_ref"].startswith("DRAP/ENF/")


def test_pdf_renders_to_bytes():
    """Smoke test the PDF rendering pipeline end-to-end."""
    from app.services.complaint_builder import compose_complaint
    from app.services.pdf_renderer import render_complaint_pdf

    letter = compose_complaint(
        pharmacy_name="Test Pharmacy",
        pharmacy_city="Lahore",
        pharmacy_area=None,
        medicine_name="Panadol",
        strength="500mg",
        drap_reg_number="DRAP-020-PCM",
        active_ingredient="Paracetamol",
        manufacturer="GSK",
        official_mrp_pkr=30,
        charged_price_pkr=80,
        incident_date="2026-05-10",
    )
    pdf = render_complaint_pdf(letter)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1500  # non-trivial content
