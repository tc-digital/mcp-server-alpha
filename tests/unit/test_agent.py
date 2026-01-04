"""Tests for research agent."""
import os

import pytest

from mcp_server_alpha.agents import ResearchAgent


def test_agent_initialization_requires_key():
    """Test that agent requires API key."""
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        del os.environ["OPENAI_API_KEY"]

    try:
        with pytest.raises(ValueError, match="OpenAI API key required"):
            ResearchAgent()
    finally:
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_agent_initialization_with_key():
    """Test agent initializes with API key."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    agent = ResearchAgent(model="gpt-4o-mini")

    assert agent.tools is not None
    assert len(agent.tools) == 4  # 4 research tools


@pytest.mark.asyncio
async def test_agent_research():
    """Test basic research functionality."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping integration test")

    agent = ResearchAgent()

    result = await agent.research("Hello!")

    assert "response" in result
    assert "reasoning_chain" in result
    assert "state" in result
    assert isinstance(result["response"], str)
