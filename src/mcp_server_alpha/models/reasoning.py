"""Reasoning and thought chain models."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReasoningType(str, Enum):
    """Types of reasoning steps."""

    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    HYPOTHESIS = "hypothesis"
    VALIDATION = "validation"
    CONCLUSION = "conclusion"


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain."""

    step_id: int = Field(..., description="Step number in sequence")
    reasoning_type: ReasoningType = Field(..., description="Type of reasoning")
    thought: str = Field(..., description="The reasoning thought")
    evidence: list[str] = Field(
        default_factory=list, description="Supporting evidence"
    )
    confidence: float = Field(default=0.5, description="Confidence in this step (0-1)")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When step was created"
    )


class ThoughtChain(BaseModel):
    """Complete reasoning chain for a query."""

    query: str = Field(..., description="Original query")
    steps: list[ReasoningStep] = Field(
        default_factory=list, description="Reasoning steps"
    )
    final_conclusion: str | None = Field(
        None, description="Final conclusion if reached"
    )
    open_questions: list[str] = Field(
        default_factory=list, description="Questions that remain open"
    )

    def add_step(
        self, reasoning_type: ReasoningType, thought: str, evidence: list[str] | None = None
    ) -> ReasoningStep:
        """Add a reasoning step to the chain."""
        step = ReasoningStep(
            step_id=len(self.steps) + 1,
            reasoning_type=reasoning_type,
            thought=thought,
            evidence=evidence or [],
        )
        self.steps.append(step)
        return step
