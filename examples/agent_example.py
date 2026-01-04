"""Example demonstrating the LangGraph agent with OpenAI integration."""
import asyncio
import os
from pathlib import Path

from mcp_server_alpha.agents import InsuranceAgent
from mcp_server_alpha.config import ConfigLoader, ProductRegistry
from mcp_server_alpha.providers import MockInsuranceProvider, ProviderRegistry


async def main():
    """Run agent example."""
    print("=== MCP Server Alpha - LangGraph Agent Example ===\n")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable not set!")
        print("\nTo run this example with real LLM:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  python examples/agent_example.py")
        print("\nOr run the basic example without LLM:")
        print("  python examples/example_workflow.py")
        return

    # 1. Set up registries
    print("1. Initializing registries...")
    product_registry = ProductRegistry()
    provider_registry = ProviderRegistry()

    # Load products
    config_dir = Path(__file__).parent / "products"
    ConfigLoader.load_from_directory(config_dir, product_registry)
    print(f"   Loaded {len(product_registry.list_products())} products")

    # Register provider
    provider = MockInsuranceProvider("mock_insurance_co")
    provider_registry.register(provider)
    print("   Registered mock insurance provider\n")

    # 2. Initialize agent
    print("2. Initializing LangGraph agent with OpenAI...")
    try:
        agent = InsuranceAgent(
            product_registry=product_registry,
            provider_registry=provider_registry,
            model="gpt-4o-mini",  # Fast and cost-effective
            temperature=0.7,
        )
        print("   ✓ Agent initialized with gpt-4o-mini\n")
    except Exception as e:
        print(f"   ✗ Failed to initialize agent: {e}")
        return

    # 3. Conversational interaction
    print("3. Starting conversational interaction...\n")
    print("=" * 60)

    conversations = [
        "Hi! I'm looking for health insurance. What options do you have?",
        "I'm 38 years old and live in California. Am I eligible?",
        "Can you give me a quote? I have 2 dependents.",
        "What other insurance products would you recommend?",
    ]

    state = None
    for i, message in enumerate(conversations, 1):
        print(f"\n👤 User: {message}")
        print("-" * 60)

        try:
            result = await agent.chat(message, state)
            response = result["response"]
            state = result["state"]

            print(f"🤖 Agent: {response}")

        except Exception as e:
            print(f"❌ Error: {e}")

        if i < len(conversations):
            print("\n" + "=" * 60)

    print("\n" + "=" * 60)
    print("\n✅ Example complete!")
    print("\nThe agent demonstrates:")
    print("  • Natural language understanding")
    print("  • Context maintenance across turns")
    print("  • Tool usage (product search, eligibility, quotes)")
    print("  • Conversational explanations")
    print("\nNote: With OPENAI_API_KEY set, the agent uses real LLM reasoning.")
    print("Without it, falls back to rule-based responses.")


async def simple_demo():
    """Simple demo without full conversation."""
    print("=== Quick Agent Demo ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to run this demo")
        return

    # Setup
    product_registry = ProductRegistry()
    provider_registry = ProviderRegistry()

    config_dir = Path(__file__).parent / "products"
    ConfigLoader.load_from_directory(config_dir, product_registry)

    provider = MockInsuranceProvider("mock_insurance_co")
    provider_registry.register(provider)

    # Create agent
    agent = InsuranceAgent(product_registry, provider_registry)

    # Single interaction
    result = await agent.chat("What health insurance products do you have?")
    print(f"Agent response: {result['response']}")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Uncomment for simple demo:
    # asyncio.run(simple_demo())
