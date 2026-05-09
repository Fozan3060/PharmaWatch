from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    user_input: str = Field(
        ...,
        min_length=5,
        description="Free-text user complaint, e.g. 'Charged Rs. 1200 for Ceftum 500mg at City Pharmacy, Saddar.'",
    )
    session_hash: str | None = Field(
        None,
        description="Anonymous one-way session hash for rate-limiting only — never identifies the user.",
    )
