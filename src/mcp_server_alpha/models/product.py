"""Product and related models."""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    """Product categories."""

    HEALTH = "health"
    DENTAL = "dental"
    VISION = "vision"
    LIFE = "life"
    DISABILITY = "disability"
    MEDICARE = "medicare"
    ANCILLARY = "ancillary"


class Qualifier(BaseModel):
    """Product qualifier/requirement."""

    name: str = Field(..., description="Qualifier name")
    description: str = Field(..., description="Human-readable description")
    field: str = Field(..., description="Consumer profile field to check")
    operator: str = Field(..., description="Comparison operator (eq, ne, gt, lt, gte, lte, in)")
    value: Any = Field(..., description="Value to compare against")

    def evaluate(self, consumer_data: dict[str, Any]) -> bool:
        """Evaluate qualifier against consumer data."""
        field_value = consumer_data.get(self.field)
        if field_value is None:
            return False

        match self.operator:
            case "eq":
                return field_value == self.value
            case "ne":
                return field_value != self.value
            case "gt":
                return field_value > self.value
            case "lt":
                return field_value < self.value
            case "gte":
                return field_value >= self.value
            case "lte":
                return field_value <= self.value
            case "in":
                return field_value in self.value
            case _:
                return False


class EligibilityRule(BaseModel):
    """Eligibility rule for a product."""

    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Human-readable description")
    qualifiers: list[Qualifier] = Field(default_factory=list)
    logic: str = Field(default="all", description="Combination logic: 'all' or 'any'")

    def evaluate(self, consumer_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Evaluate eligibility rule.

        Returns:
            Tuple of (is_eligible, reasons) where reasons explain why rule passed/failed
        """
        results = [q.evaluate(consumer_data) for q in self.qualifiers]
        reasons = []

        if self.logic == "all":
            is_eligible = all(results)
            for i, (qualifier, result) in enumerate(zip(self.qualifiers, results)):
                if not result:
                    reasons.append(f"{qualifier.name}: {qualifier.description}")
        else:  # any
            is_eligible = any(results)
            if not is_eligible:
                reasons.append(f"None of the qualifiers met for rule: {self.name}")

        return is_eligible, reasons


class Disclaimer(BaseModel):
    """Compliance disclaimer."""

    type: str = Field(..., description="Disclaimer type (e.g., 'compliance', 'warning')")
    title: str = Field(..., description="Disclaimer title")
    content: str = Field(..., description="Disclaimer content")
    required_acknowledgment: bool = Field(
        default=False, description="Whether user must acknowledge"
    )
    display_order: int = Field(default=0, description="Order to display disclaimers")


class EnrollmentFlow(BaseModel):
    """Multi-step enrollment flow definition."""

    step_id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    required_fields: list[str] = Field(
        default_factory=list, description="Fields required in this step"
    )
    optional_fields: list[str] = Field(
        default_factory=list, description="Optional fields in this step"
    )
    next_step: str | None = Field(None, description="Next step ID or None if final")
    condition: dict[str, Any] | None = Field(
        None, description="Conditional logic for branching"
    )


class Product(BaseModel):
    """Insurance product definition."""

    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    category: ProductCategory = Field(..., description="Product category")
    provider_id: str = Field(..., description="Provider/carrier identifier")
    description: str = Field(..., description="Product description")
    eligibility_rules: list[EligibilityRule] = Field(
        default_factory=list, description="Eligibility rules"
    )
    disclaimers: list[Disclaimer] = Field(default_factory=list, description="Disclaimers")
    enrollment_flow: list[EnrollmentFlow] = Field(
        default_factory=list, description="Enrollment steps"
    )
    cross_sell_products: list[str] = Field(
        default_factory=list, description="Compatible product IDs for cross-sell"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional product metadata"
    )
    active: bool = Field(default=True, description="Whether product is active")

    def check_eligibility(self, consumer_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Check if consumer is eligible for this product.

        Returns:
            Tuple of (is_eligible, reasons)
        """
        all_reasons = []
        for rule in self.eligibility_rules:
            is_eligible, reasons = rule.evaluate(consumer_data)
            if not is_eligible:
                all_reasons.extend(reasons)

        return len(all_reasons) == 0, all_reasons
