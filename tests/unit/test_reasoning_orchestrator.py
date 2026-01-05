"""Tests for reasoning orchestrator."""
import os

import pytest

from mcp_server_alpha.agents import ReasoningOrchestrator


def test_orchestrator_initialization_requires_key():
    """Test that orchestrator requires API key."""
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        del os.environ["OPENAI_API_KEY"]

    try:
        with pytest.raises(ValueError, match="OpenAI API key required"):
            ReasoningOrchestrator()
    finally:
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_orchestrator_initialization_with_key():
    """Test orchestrator initializes with API key."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    orchestrator = ReasoningOrchestrator(model="gpt-4o-mini")

    assert orchestrator.agent is not None
    assert orchestrator.agent.tools is not None


@pytest.mark.asyncio
async def test_orchestrator_execute():
    """Test basic orchestrator execution."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping integration test")

    orchestrator = ReasoningOrchestrator()

    result = await orchestrator.execute("Calculate 10 + 20")

    assert "result" in result
    assert "steps" in result
    assert "tool_calls" in result
    assert "reasoning" in result
    assert isinstance(result["result"], str)
    assert isinstance(result["steps"], list)
    assert isinstance(result["tool_calls"], list)


@pytest.mark.asyncio
async def test_orchestrator_extract_steps():
    """Test step extraction from reasoning chain."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    orchestrator = ReasoningOrchestrator()

    # Mock reasoning chain
    reasoning_chain = [
        "💭 I need to search for information about Python",
        "🔧 Using web_search tool: {'query': 'Python programming'}",
        "💭 Based on the results, I can conclude...",
    ]

    steps = orchestrator._extract_steps(reasoning_chain)

    assert len(steps) == 3
    assert steps[0]["type"] == "reasoning"
    assert steps[1]["type"] == "tool_execution"
    assert steps[2]["type"] == "reasoning"


@pytest.mark.asyncio
async def test_orchestrator_extract_tool_calls():
    """Test tool call extraction from reasoning chain."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    orchestrator = ReasoningOrchestrator()

    # Mock reasoning chain
    reasoning_chain = [
        "💭 I need to calculate something",
        '🔧 Using calculate tool: {"expression": "2 + 2"}',
        "💭 The result is 4",
    ]

    tool_calls = orchestrator._extract_tool_calls(reasoning_chain)

    assert len(tool_calls) == 1
    assert tool_calls[0]["tool"] == "calculate"
    assert "expression" in tool_calls[0]["arguments"]


@pytest.mark.asyncio
async def test_orchestrator_with_streaming():
    """Test orchestrator with streaming (future feature)."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping integration test")

    orchestrator = ReasoningOrchestrator()

    result = await orchestrator.execute_with_streaming("Hello!")

    assert "result" in result
    assert "streaming_enabled" in result
    assert result["streaming_enabled"] is False  # Not yet implemented
