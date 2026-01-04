"""Consumer and profile models."""
from datetime import date

from pydantic import BaseModel, Field


class ConsumerProfile(BaseModel):
    """Consumer profile with relevant attributes for eligibility."""

    age: int = Field(..., description="Consumer age")
    state: str = Field(..., description="State of residence")
    zip_code: str = Field(..., description="ZIP code")
    income: int | None = Field(None, description="Annual income")
    employment_status: str | None = Field(None, description="Employment status")
    household_size: int = Field(default=1, description="Number in household")
    has_medicare: bool = Field(default=False, description="Has Medicare coverage")
    has_medicaid: bool = Field(default=False, description="Has Medicaid coverage")
    tobacco_user: bool = Field(default=False, description="Tobacco user")
    pre_existing_conditions: list[str] = Field(
        default_factory=list, description="Pre-existing conditions"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for evaluation."""
        return self.model_dump()


class Consumer(BaseModel):
    """Consumer information."""

    id: str = Field(..., description="Consumer ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: str | None = Field(None, description="Phone number")
    date_of_birth: date = Field(..., description="Date of birth")
    profile: ConsumerProfile = Field(..., description="Consumer profile")
