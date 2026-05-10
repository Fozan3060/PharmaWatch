from fastapi import APIRouter, HTTPException

from app.api.schemas.reports import CommunityReportResponse, CommunityReportSubmission
from app.data.firebase import reports_repo
from app.normalization.pharmacy_names import make_pharmacy_id
from app.services.pattern_detection import aggregate_for_heatmap, classify

router = APIRouter()


@router.get("/heatmap")
async def heatmap() -> dict:
    """Initial heatmap load. The frontend subscribes to Firestore directly for live updates."""
    reports = reports_repo.all_recent_reports(days=30)
    return {"pharmacies": aggregate_for_heatmap(reports)}


@router.post("/submit", response_model=CommunityReportResponse)
async def submit_report(req: CommunityReportSubmission) -> CommunityReportResponse:
    """User-initiated anonymous submission. The agent does NOT auto-log; the
    user explicitly clicks Submit after reviewing the Investigation Report.

    Server-side guardrails:
    - charged_price must be strictly greater than the DRAP MRP (no underpayment "reports")
    - both prices must be reasonable (Pydantic schema bounds)
    """
    if req.charged_price_pkr <= req.official_mrp_pkr:
        raise HTTPException(
            status_code=400,
            detail="charged_price_pkr must be greater than official_mrp_pkr — only "
            "verified overcharges can be submitted to the community heatmap.",
        )

    pharmacy_id = make_pharmacy_id(req.pharmacy_name, req.pharmacy_area, req.pharmacy_city)
    overcharge_amt = round(req.charged_price_pkr - req.official_mrp_pkr, 2)
    overcharge_pct = round((overcharge_amt / req.official_mrp_pkr) * 100, 1)

    report_id = reports_repo.add_report(
        {
            "pharmacyId": pharmacy_id,
            "pharmacyName": req.pharmacy_name,
            "area": req.pharmacy_area,
            "city": req.pharmacy_city,
            "medicine": req.medicine,
            "officialMRP": req.official_mrp_pkr,
            "chargedPrice": req.charged_price_pkr,
            "overchargeAmt": overcharge_amt,
            "overchargePct": overcharge_pct,
        }
    )

    pharmacy_reports = reports_repo.reports_for_pharmacy(pharmacy_id)
    count = len(pharmacy_reports)
    return CommunityReportResponse(
        report_id=report_id,
        pharmacy_id=pharmacy_id,
        pharmacy_total_reports_30d=count,
        classification=classify(count),
    )
