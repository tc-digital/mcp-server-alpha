"""Example demonstrating the Research Assistant agent."""
import asyncio
import os

from mcp_server_alpha.agents import ResearchAgent


async def main():
    """Run research assistant example."""
    print("=== Research Assistant with LangGraph ===\n")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable not set!")
        print("\nTo run this example:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  python examples/research_example.py")
        return

    # Initialize agent
    print("1. Initializing Research Assistant agent with OpenAI...")
    try:
        agent = ResearchAgent(
            model="gpt-4o-mini",  # Fast and cost-effective
            temperature=0.7,
        )
        print("   ✓ Agent initialized with gpt-4o-mini\n")
    except Exception as e:
        print(f"   ✗ Failed to initialize agent: {e}")
        return

    # Example research queries
    print("2. Starting research demonstration...\n")
    print("=" * 70)

    research_queries = [
        "What are the key differences between machine learning and deep learning?",
        "Calculate the compound interest on $10,000 invested at 5% annual rate for 3 years",
        "Analyze this dataset: [10, 15, 20, 25, 30, 35, 40] and tell me the statistics",
    ]

    for i, query in enumerate(research_queries, 1):
        print(f"\n📋 Research Query {i}:")
        print(f"   {query}")
        print("-" * 70)

        try:
            result = await agent.research(query)
            response = result["response"]
            reasoning = result["reasoning_chain"]

            print(f"\n🤖 Agent Response:")
            print(f"   {response}\n")

            if reasoning:
                print("💭 Reasoning Chain:")
                for step in reasoning:
                    print(f"   {step}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        if i < len(research_queries):
            print("\n" + "=" * 70)

    print("\n" + "=" * 70)
    print("\n✅ Research demonstration complete!")
    print("\n📚 The agent demonstrates:")
    print("  • Autonomous research with web search")
    print("  • Mathematical calculations")
    print("  • Data analysis and statistics")
    print("  • Visible reasoning chain showing thought process")
    print("  • Tool orchestration based on query type")
    print("\n💡 The agent can research any topic and use tools as needed!")


async def interactive_mode():
    """Interactive research mode."""
    print("=== Interactive Research Assistant ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to use interactive mode")
        return

    agent = ResearchAgent()
    print("Agent ready! Ask me anything (type 'quit' to exit):\n")

    state = None
    while True:
        query = input("You: ")
        if query.lower() in ["quit", "exit", "q"]:
            break

        try:
            result = await agent.research(query, state)
            state = result["state"]

            print(f"\nAgent: {result['response']}\n")

            if result["reasoning_chain"]:
                print("Reasoning:")
                for step in result["reasoning_chain"]:
                    print(f"  {step}")
                print()

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(main())

    # Uncomment for interactive mode:
    # asyncio.run(interactive_mode())
