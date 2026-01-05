"""Reasoning agent orchestrator for MCP tool coordination."""
import json
from typing import Any

from .research_agent import ResearchAgent


class ReasoningOrchestrator:
    """
    Meta-tool orchestrator using LangGraph for reasoning and tool coordination.

    This orchestrator:
    - Receives complex natural language instructions from MCP clients
    - Uses LangGraph to plan and execute a sequence of tool calls
    - Streams step-by-step progress updates for transparency
    - Makes branching decisions based on intermediate results
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize the reasoning orchestrator.

        Args:
            api_key: OpenAI API key (or None to use OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: LLM temperature for response generation
        """
        self.agent = ResearchAgent(api_key=api_key, model=model, temperature=temperature)

    async def execute(
        self, goal: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute a goal using reasoning and tool orchestration.

        Args:
            goal: Natural language description of the goal to achieve
            context: Optional context from previous executions

        Returns:
            Dict with:
                - result: Final result/answer
                - steps: List of execution steps taken
                - tool_calls: List of tools used
                - reasoning: Reasoning chain
        """
        # Add orchestrator-specific system prompt
        enhanced_goal = self._enhance_goal_with_context(goal, context)

        # Execute using the research agent
        result = await self.agent.research(enhanced_goal)

        # Extract execution details
        steps = self._extract_steps(result["reasoning_chain"])
        tool_calls = self._extract_tool_calls(result["reasoning_chain"])

        return {
            "result": result["response"],
            "steps": steps,
            "tool_calls": tool_calls,
            "reasoning": result["reasoning_chain"],
            "state": result["state"],
        }

    def _enhance_goal_with_context(
        self, goal: str, context: dict[str, Any] | None
    ) -> str:
        """Add orchestration context to the goal."""
        enhanced = (
            "As an autonomous reasoning agent, analyze this goal and determine the "
            "best sequence of actions to achieve it:\n\n"
            f"GOAL: {goal}\n\n"
            "Available tools:\n"
            "- web_search: Search for information online\n"
            "- calculate: Perform mathematical calculations\n"
            "- analyze_data: Analyze datasets and find patterns\n"
            "- summarize_text: Summarize long text content\n\n"
            "Think step-by-step:\n"
            "1. Break down the goal into actionable sub-tasks\n"
            "2. Identify which tools are needed for each sub-task\n"
            "3. Execute tools in logical order\n"
            "4. Synthesize results into a final answer\n\n"
            "Show your reasoning process clearly at each step."
        )

        if context:
            enhanced += f"\n\nPrevious context:\n{json.dumps(context, indent=2)}"

        return enhanced

    def _extract_steps(self, reasoning_chain: list[str]) -> list[dict[str, str]]:
        """Extract execution steps from reasoning chain."""
        steps = []
        step_num = 1

        for item in reasoning_chain:
            if "🔧 Using" in item:
                # Tool execution step
                steps.append({
                    "step": step_num,
                    "type": "tool_execution",
                    "description": item,
                })
                step_num += 1
            elif "💭" in item:
                # Reasoning step
                steps.append({
                    "step": step_num,
                    "type": "reasoning",
                    "description": item,
                })
                step_num += 1

        return steps

    def _extract_tool_calls(self, reasoning_chain: list[str]) -> list[dict[str, Any]]:
        """Extract tool calls from reasoning chain."""
        tool_calls = []

        for item in reasoning_chain:
            if "🔧 Using" in item and " tool:" in item:
                # Parse tool call - Note: This relies on the agent formatting
                # tool calls with specific emoji and text patterns.
                # Future improvement: use structured JSON markers
                parts = item.split(" tool:")
                if len(parts) == 2:
                    tool_name = parts[0].replace("🔧 Using ", "").strip()
                    try:
                        args = json.loads(parts[1].strip()) if parts[1].strip() else {}
                    except json.JSONDecodeError as e:
                        # Log parsing issue and store raw text for debugging
                        # In production, this should be logged to monitoring system
                        args = {
                            "raw": parts[1].strip(),
                            "parse_error": str(e),
                        }

                    tool_calls.append({
                        "tool": tool_name,
                        "arguments": args,
                    })

        return tool_calls

    async def execute_with_streaming(
        self, goal: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute goal with streaming progress updates.

        This is a future enhancement that would stream intermediate results.
        For now, it wraps the regular execute method.

        Args:
            goal: Natural language description of the goal
            context: Optional context from previous executions

        Returns:
            Execution results with streaming metadata
        """
        result = await self.execute(goal, context)

        # Add streaming metadata
        result["streaming_enabled"] = False
        result["message"] = (
            "Streaming support coming in future version. "
            "See steps array for execution progress."
        )

        return result
