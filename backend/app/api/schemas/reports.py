from pydantic import BaseModel, Field


class CommunityReportSubmission(BaseModel):
    """User-initiated submission to the public fraud heatmap."""

    pharmacy_name: str = Field(..., min_length=2, max_length=120)
    pharmacy_area: str | None = Field(None, max_length=120)
    pharmacy_city: str = Field(..., min_length=2, max_length=80)
    medicine: str = Field(..., min_length=2, max_length=120)
    official_mrp_pkr: float = Field(..., gt=0, lt=1_000_000)
    charged_price_pkr: float = Field(..., gt=0, lt=1_000_000)


class CommunityReportResponse(BaseModel):
    report_id: str
    pharmacy_id: str
    pharmacy_total_reports_30d: int
    classification: str
