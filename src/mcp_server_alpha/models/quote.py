"""Quote models."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    """Request for a product quote."""

    product_id: str = Field(..., description="Product ID to quote")
    consumer_id: str = Field(..., description="Consumer ID")
    coverage_amount: Decimal | None = Field(None, description="Requested coverage amount")
    dependents: int = Field(default=0, description="Number of dependents")
    effective_date: datetime | None = Field(None, description="Desired effective date")
    options: dict[str, str] = Field(default_factory=dict, description="Additional options")


class Quote(BaseModel):
    """Insurance quote."""

    quote_id: str = Field(..., description="Unique quote ID")
    product_id: str = Field(..., description="Product ID")
    consumer_id: str = Field(..., description="Consumer ID")
    monthly_premium: Decimal = Field(..., description="Monthly premium amount")
    deductible: Decimal | None = Field(None, description="Deductible amount")
    coverage_amount: Decimal | None = Field(None, description="Coverage amount")
    effective_date: datetime = Field(..., description="Coverage effective date")
    expiration_date: datetime = Field(..., description="Quote expiration date")
    details: dict[str, str] = Field(default_factory=dict, description="Quote details")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(), description="Quote creation time"
    )


class QuoteResponse(BaseModel):
    """Response containing quote information."""

    success: bool = Field(..., description="Whether quote was successful")
    quote: Quote | None = Field(None, description="Quote if successful")
    error: str | None = Field(None, description="Error message if unsuccessful")
    reasons: list[str] = Field(default_factory=list, description="Additional details")
