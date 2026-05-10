from app.agent.tools import all_tools, dispatch


def test_get_pharmacy_reports_registered():
    names = {t.name for t in all_tools()}
    assert "get_pharmacy_reports" in names


def test_log_community_report_not_registered():
    """The agent must not have a tool that writes community reports — the user
    submits manually after reviewing the investigation."""
    names = {t.name for t in all_tools()}
    assert "log_community_report" not in names


async def test_get_reports_for_unknown_pharmacy():
    result = await dispatch("get_pharmacy_reports",
                            pharmacy_name="Nonexistent", city="Karachi")
    assert result["report_count"] == 0
    assert result["classification"] == "clean"
