"""Tests for LangGraph agent integration."""
import os

import pytest

from mcp_server_alpha.agents import InsuranceAgent
from mcp_server_alpha.config import ProductRegistry
from mcp_server_alpha.providers import MockInsuranceProvider, ProviderRegistry


@pytest.fixture
def registries():
    """Create test registries."""
    product_registry = ProductRegistry()
    provider_registry = ProviderRegistry()

    # Register mock provider
    provider = MockInsuranceProvider("test_provider")
    provider_registry.register(provider)

    return product_registry, provider_registry


def test_agent_initialization_without_key(registries):
    """Test that agent requires API key."""
    product_registry, provider_registry = registries

    # Temporarily remove API key if present
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        del os.environ["OPENAI_API_KEY"]

    try:
        with pytest.raises(ValueError, match="OpenAI API key required"):
            InsuranceAgent(product_registry, provider_registry)
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_agent_initialization_with_key(registries):
    """Test agent initializes with API key."""
    product_registry, provider_registry = registries

    # Skip if no API key available
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    agent = InsuranceAgent(
        product_registry, provider_registry, model="gpt-4o-mini"
    )

    assert agent.product_registry == product_registry
    assert agent.provider_registry == provider_registry
    assert agent.tools is not None
    assert len(agent.tools) == 4  # 4 tools available


def test_create_sample_consumer(registries):
    """Test helper to create consumer from parameters."""
    product_registry, provider_registry = registries

    # Skip if no API key available
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    agent = InsuranceAgent(product_registry, provider_registry)

    consumer = agent.create_sample_consumer(
        age=35,
        state="CA",
        zip_code="90210",
        first_name="Jane",
        last_name="Doe",
    )

    assert consumer.profile.age == 35
    assert consumer.profile.state == "CA"
    assert consumer.profile.zip_code == "90210"
    assert consumer.first_name == "Jane"
    assert consumer.last_name == "Doe"


@pytest.mark.asyncio
async def test_agent_chat_basic(registries):
    """Test basic agent chat (requires API key)."""
    product_registry, provider_registry = registries

    # Skip if no API key available
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping integration test")

    agent = InsuranceAgent(product_registry, provider_registry)

    result = await agent.chat("Hello!")

    assert "response" in result
    assert "state" in result
    assert isinstance(result["response"], str)
    assert len(result["response"]) > 0
