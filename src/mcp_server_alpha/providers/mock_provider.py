"""Mock insurance provider for testing and examples."""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from ..models import Consumer, Product, Quote, QuoteRequest
from .base import BaseProvider


class MockInsuranceProvider(BaseProvider):
    """Mock insurance provider implementation."""

    async def check_eligibility(
        self, product: Product, consumer: Consumer
    ) -> tuple[bool, list[str]]:
        """Check eligibility using product rules and mock provider logic."""
        # First check product-level eligibility
        is_eligible, reasons = product.check_eligibility(consumer.profile.to_dict())

        # Add provider-specific checks
        if consumer.profile.age < 18:
            is_eligible = False
            reasons.append("Consumer must be 18 or older")

        if not is_eligible:
            return False, reasons

        return True, ["All eligibility requirements met"]

    async def get_quote(self, quote_request: QuoteRequest, consumer: Consumer) -> Quote:
        """Generate a mock quote."""
        # Calculate mock premium based on age and product
        base_premium = Decimal("100.00")
        age_factor = Decimal(str(consumer.profile.age / 50))
        tobacco_factor = Decimal("1.5") if consumer.profile.tobacco_user else Decimal("1.0")

        monthly_premium = base_premium * age_factor * tobacco_factor
        monthly_premium = monthly_premium.quantize(Decimal("0.01"))

        # Add dependent costs
        if quote_request.dependents > 0:
            dependent_cost = Decimal(str(quote_request.dependents * 50))
            monthly_premium += dependent_cost

        effective_date = quote_request.effective_date or datetime.now()
        expiration_date = effective_date + timedelta(days=30)

        quote = Quote(
            quote_id=str(uuid.uuid4()),
            product_id=quote_request.product_id,
            consumer_id=quote_request.consumer_id,
            monthly_premium=monthly_premium,
            deductible=Decimal("1000.00"),
            coverage_amount=quote_request.coverage_amount or Decimal("50000.00"),
            effective_date=effective_date,
            expiration_date=expiration_date,
            details={
                "provider": self.provider_id,
                "coverage_type": "individual" if quote_request.dependents == 0 else "family",
                "network": "PPO",
            },
        )

        return quote

    async def initiate_enrollment(
        self, quote: Quote, consumer: Consumer, enrollment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Initiate mock enrollment."""
        enrollment_id = str(uuid.uuid4())

        return {
            "success": True,
            "enrollment_id": enrollment_id,
            "status": "pending",
            "next_steps": [
                "Submit payment information",
                "Upload required documents",
                "E-signature required",
            ],
            "estimated_completion": (datetime.now() + timedelta(days=3)).isoformat(),
        }

    async def get_enrollment_status(self, enrollment_id: str) -> dict[str, Any]:
        """Get mock enrollment status."""
        return {
            "enrollment_id": enrollment_id,
            "status": "pending",
            "progress": 0.33,
            "current_step": "awaiting_payment",
            "updated_at": datetime.now().isoformat(),
        }
