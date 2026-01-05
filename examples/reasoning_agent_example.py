"""Example demonstrating the Reasoning Agent Orchestrator."""
import asyncio
import json
import os

from mcp_server_alpha.agents import ReasoningOrchestrator


async def main():
    """Run reasoning agent orchestrator example."""
    print("=== Reasoning Agent Orchestrator with LangGraph ===\n")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable not set!")
        print("\nTo run this example:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  python examples/reasoning_agent_example.py")
        return

    # Initialize orchestrator
    print("1. Initializing Reasoning Agent Orchestrator with OpenAI...")
    try:
        orchestrator = ReasoningOrchestrator(
            model="gpt-4o-mini",  # Fast and cost-effective
            temperature=0.7,
        )
        print("   ✓ Orchestrator initialized with gpt-4o-mini\n")
    except Exception as e:
        print(f"   ✗ Failed to initialize orchestrator: {e}")
        return

    # Example goals that require multi-tool orchestration
    print("2. Starting reasoning agent demonstration...\n")
    print("=" * 80)

    goals = [
        "Research machine learning trends and calculate the average growth rate",
        "Analyze this dataset: [100, 150, 200, 250, 300] and summarize the findings",
        "Find information about quantum computing and provide a brief summary",
    ]

    for i, goal in enumerate(goals, 1):
        print(f"\n🎯 Goal {i}:")
        print(f"   {goal}")
        print("-" * 80)

        try:
            result = await orchestrator.execute(goal)

            # Display execution summary
            print(f"\n📊 Execution Summary:")
            print(f"   • Total Steps: {len(result['steps'])}")
            print(f"   • Tools Used: {len(result['tool_calls'])}")
            if result["tool_calls"]:
                tools_used = [tc["tool"] for tc in result["tool_calls"]]
                print(f"   • Tool List: {', '.join(tools_used)}")

            # Display final result
            print(f"\n🎉 Result:")
            print(f"   {result['result']}\n")

            # Display execution steps (limited to first 5 for brevity)
            if result["steps"]:
                print("📋 Execution Steps (first 5):")
                for step in result["steps"][:5]:
                    step_type = "🔧" if step["type"] == "tool_execution" else "💭"
                    desc = step["description"][:100] + "..." if len(step["description"]) > 100 else step["description"]
                    print(f"   {step_type} Step {step['step']}: {desc}")
                
                if len(result["steps"]) > 5:
                    print(f"   ... and {len(result['steps']) - 5} more steps")

            # Display reasoning chain (limited to first 3 for brevity)
            if result["reasoning"]:
                print("\n💭 Reasoning Chain (first 3):")
                for reasoning in result["reasoning"][:3]:
                    print(f"   {reasoning[:120]}...")
                
                if len(result["reasoning"]) > 3:
                    print(f"   ... and {len(result['reasoning']) - 3} more reasoning steps")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        if i < len(goals):
            print("\n" + "=" * 80)

    print("\n" + "=" * 80)
    print("\n✅ Reasoning agent demonstration complete!")
    print("\n📚 The reasoning agent demonstrates:")
    print("  • Autonomous goal decomposition and planning")
    print("  • Multi-tool orchestration (search, calculator, analyzer, summarizer)")
    print("  • Step-by-step execution tracking")
    print("  • Visible reasoning chain showing decision-making")
    print("  • Branching logic based on intermediate results")
    print("\n💡 Use this agent for complex tasks requiring multiple tools and decisions!")


async def interactive_mode():
    """Interactive reasoning agent mode."""
    print("=== Interactive Reasoning Agent ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to use interactive mode")
        return

    orchestrator = ReasoningOrchestrator()
    print("Reasoning Agent ready! Describe your goal (type 'quit' to exit):\n")

    context = None
    while True:
        goal = input("Goal: ")
        if goal.lower() in ["quit", "exit", "q"]:
            break

        try:
            result = await orchestrator.execute(goal, context)
            
            print(f"\n🎉 Result: {result['result']}")
            print(f"\n📊 Summary: {len(result['steps'])} steps, {len(result['tool_calls'])} tools used\n")

            if result["reasoning"]:
                print("💭 Reasoning (abbreviated):")
                for reasoning in result["reasoning"][:3]:
                    print(f"  {reasoning[:120]}...")
                print()

            # Optional: maintain context for follow-up goals
            # context = result.get("state")

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(main())

    # Uncomment for interactive mode:
    # asyncio.run(interactive_mode())
