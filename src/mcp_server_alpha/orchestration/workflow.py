"""Workflow orchestration engine."""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..models import Consumer, Product, Quote


class WorkflowState(str, Enum):
    """Workflow states."""

    INITIATED = "initiated"
    ELIGIBILITY_CHECK = "eligibility_check"
    QUOTE_GENERATION = "quote_generation"
    CROSS_SELL = "cross_sell"
    ENROLLMENT = "enrollment"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowContext(BaseModel):
    """Context for workflow execution."""

    workflow_id: str = Field(..., description="Unique workflow ID")
    state: WorkflowState = Field(default=WorkflowState.INITIATED)
    consumer: Consumer | None = None
    product: Product | None = None
    quote: Quote | None = None
    cross_sell_products: list[Product] = Field(default_factory=list)
    enrollment_data: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowEngine:
    """
    Workflow orchestration engine for multi-step processes.

    This engine manages the flow from initial contact through eligibility,
    quoting, cross-sell, and enrollment.
    """

    def __init__(self) -> None:
        """Initialize workflow engine."""
        self._workflows: dict[str, WorkflowContext] = {}

    def create_workflow(self, workflow_id: str, consumer: Consumer) -> WorkflowContext:
        """Create a new workflow."""
        context = WorkflowContext(workflow_id=workflow_id, consumer=consumer)
        self._workflows[workflow_id] = context
        return context

    def get_workflow(self, workflow_id: str) -> WorkflowContext | None:
        """Get workflow by ID."""
        return self._workflows.get(workflow_id)

    async def process_eligibility(
        self, workflow_id: str, product: Product, eligibility_result: tuple[bool, list[str]]
    ) -> WorkflowContext:
        """Process eligibility check result."""
        context = self.get_workflow(workflow_id)
        if not context:
            raise ValueError(f"Workflow {workflow_id} not found")

        context.product = product
        is_eligible, reasons = eligibility_result

        if is_eligible:
            context.state = WorkflowState.QUOTE_GENERATION
        else:
            context.state = WorkflowState.FAILED
            context.errors.extend(reasons)

        return context

    async def process_quote(self, workflow_id: str, quote: Quote) -> WorkflowContext:
        """Process quote generation result."""
        context = self.get_workflow(workflow_id)
        if not context:
            raise ValueError(f"Workflow {workflow_id} not found")

        context.quote = quote
        context.state = WorkflowState.CROSS_SELL
        return context

    async def process_cross_sell(
        self, workflow_id: str, cross_sell_products: list[Product]
    ) -> WorkflowContext:
        """Process cross-sell recommendations."""
        context = self.get_workflow(workflow_id)
        if not context:
            raise ValueError(f"Workflow {workflow_id} not found")

        context.cross_sell_products = cross_sell_products
        context.state = WorkflowState.ENROLLMENT
        return context

    async def process_enrollment(
        self, workflow_id: str, enrollment_result: dict[str, Any]
    ) -> WorkflowContext:
        """Process enrollment initiation result."""
        context = self.get_workflow(workflow_id)
        if not context:
            raise ValueError(f"Workflow {workflow_id} not found")

        context.enrollment_data = enrollment_result

        if enrollment_result.get("success"):
            context.state = WorkflowState.COMPLETED
        else:
            context.state = WorkflowState.FAILED
            context.errors.append(enrollment_result.get("error", "Enrollment failed"))

        return context

    def clear(self) -> None:
        """Clear all workflows (useful for testing)."""
        self._workflows.clear()
