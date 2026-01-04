"""Research-related models."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResearchQueryType(str, Enum):
    """Types of research queries."""

    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    EXPLORATORY = "exploratory"


class Source(BaseModel):
    """Information source."""

    url: str | None = Field(None, description="URL of the source")
    title: str = Field(..., description="Title of the source")
    content: str = Field(..., description="Content or excerpt")
    source_type: str = Field(default="web", description="Type of source (web, document, api, etc.)")
    reliability_score: float = Field(default=0.5, description="Reliability score 0-1")
    timestamp: datetime = Field(default_factory=datetime.now, description="When sourced")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ResearchQuery(BaseModel):
    """A research query from the user."""

    query: str = Field(..., description="The research question or topic")
    query_type: ResearchQueryType = Field(
        default=ResearchQueryType.EXPLORATORY, description="Type of research query"
    )
    depth: int = Field(default=1, description="Research depth (1-5, more = deeper)")
    max_sources: int = Field(default=5, description="Maximum number of sources to gather")
    focus_areas: list[str] = Field(
        default_factory=list, description="Specific areas to focus on"
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Research constraints (time, language, etc.)"
    )


class ResearchResult(BaseModel):
    """Result of a research task."""

    query: str = Field(..., description="Original query")
    summary: str = Field(..., description="Summary of findings")
    sources: list[Source] = Field(default_factory=list, description="Sources used")
    key_findings: list[str] = Field(default_factory=list, description="Key findings")
    confidence_score: float = Field(
        default=0.5, description="Confidence in results (0-1)"
    )
    reasoning_chain: list[str] = Field(
        default_factory=list, description="Reasoning steps taken"
    )
    follow_up_questions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When result was created"
    )


class ResearchTask(BaseModel):
    """A decomposed research sub-task."""

    task_id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")
    tool_name: str = Field(..., description="Tool to use for this task")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Task IDs this depends on"
    )
    status: str = Field(default="pending", description="Task status")
    result: Any = Field(None, description="Task result")
