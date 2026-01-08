"""Main MCP server implementation for Research Assistant."""
import sys
from typing import Any

from fastmcp import FastMCP

from .agents.reasoning_orchestrator import ReasoningOrchestrator
from .tools.analyzer import analyze_data_tool
from .tools.calculator import calculate_tool
from .tools.search import web_search_tool
from .tools.send_email import send_email_tool
from .tools.summarizer import summarize_tool
from .tools.weather import weather_forecast_tool

sys.stderr.write("=== ALL IMPORTS SUCCESSFUL ===\n")
sys.stderr.flush()

# Create FastMCP server instance
mcp = FastMCP("mcp-server-alpha-research")

# Initialize reasoning orchestrator (lazy initialization to avoid
# API key requirements at startup)
_orchestrator: ReasoningOrchestrator | None = None


@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search the web for information on a given query.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)

    Returns:
        List of search results with title, url, and snippet
    """
    result = await web_search_tool(query=query, max_results=max_results)
    return result


@mcp.tool()
async def calculate(expression: str) -> dict[str, Any]:
    """Perform mathematical calculations and evaluate expressions.

    Args:
        expression: Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', 'sqrt(16)')

    Returns:
        Dictionary containing the calculation result
    """
    result = await calculate_tool(expression=expression)
    return result


@mcp.tool()
async def analyze_data(data: list[float], analysis_type: str = "statistical") -> dict[str, Any]:
    """Analyze numerical data and provide statistical insights.

    Args:
        data: Array of numerical values to analyze
        analysis_type: Type of analysis to perform ('statistical', 'trends', or 'patterns')

    Returns:
        Dictionary containing analysis results
    """
    result = await analyze_data_tool(data=data, analysis_type=analysis_type)
    return result


@mcp.tool()
async def summarize_text(text: str, max_length: int = 100) -> dict[str, Any]:
    """Summarize long text into key points.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary in words (default: 100)

    Returns:
        Dictionary containing the summary and metadata
    """
    result = await summarize_tool(text=text, max_length=max_length)
    return result


@mcp.tool()
async def weather_forecast(location: str, forecast_type: str = "forecast") -> dict[str, Any]:
    """Get weather forecast for a location using weather.gov API.

    Supports US locations only.

    Args:
        location: Location as 5-digit US zip code (e.g., '10001') or
                  latitude,longitude (e.g., '39.7456,-97.0892')
        forecast_type: Type of forecast - 'forecast' for 12-hour periods (default),
                      'hourly' for hourly forecast

    Returns:
        Dictionary containing weather forecast data
    """
    result = await weather_forecast_tool(location=location, forecast_type=forecast_type)
    return result


@mcp.tool()
async def send_email(to_email: str, subject: str, body: str) -> dict[str, Any]:
    """Send an email by triggering a Power Automate flow via HTTP POST webhook.

    Requires POWER_AUTOMATE_WEBHOOK_URL environment variable to be configured.

    Args:
        to_email: Recipient's email address (required, must be valid email format)
        subject: Email subject (required, max 500 characters)
        body: Email body content (required, max 50,000 characters)

    Returns:
        Dictionary containing status and details of the email send operation
    """
    result = await send_email_tool(to_email=to_email, subject=subject, body=body)
    return result


@mcp.tool()
async def reasoning_agent(goal: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute complex multi-step tasks using an autonomous reasoning agent.

    Powered by LangGraph, the agent analyzes your goal, plans a sequence of actions,
    orchestrates other MCP tools, and provides step-by-step progress updates with
    visible reasoning. Use this for tasks requiring multiple tools or complex
    decision-making. Requires OPENAI_API_KEY environment variable.

    Args:
        goal: Natural language description of the goal to achieve. Be specific about
              what you want the agent to do. Example: 'Research renewable energy trends,
              analyze the data, and calculate the growth rate over the last 5 years.'
        context: Optional context from previous agent executions to maintain continuity
                across related tasks

    Returns:
        Dictionary containing execution results, steps, and reasoning chain
    """
    global _orchestrator

    # Lazy initialization of orchestrator
    if _orchestrator is None:
        try:
            _orchestrator = ReasoningOrchestrator()
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": (
                    "Reasoning agent requires OPENAI_API_KEY "
                    "environment variable to be set."
                ),
            }

    # Execute the goal using reasoning orchestrator
    result = await _orchestrator.execute(goal=goal, context=context)

    # Format result for MCP response
    formatted_result = {
        "success": True,
        "result": result["result"],
        "execution_summary": {
            "total_steps": len(result["steps"]),
            "tools_used": [tc.get("tool", "unknown") for tc in result["tool_calls"]],
            "tool_count": len(result["tool_calls"]),
        },
        "steps": result["steps"],
        "tool_calls": result["tool_calls"],
        "reasoning_chain": result["reasoning"],
    }

    return formatted_result


def main() -> None:
    """Entry point for the MCP server."""
    sys.stderr.write("=== MAIN FUNCTION CALLED ===\n")
    sys.stderr.flush()

    try:
        sys.stderr.write("=== STARTING SERVER WITH FASTMCP ===\n")
        sys.stderr.flush()

        # Run the FastMCP server using stdio transport
        mcp.run()

        sys.stderr.write("=== SERVER RUN COMPLETED ===\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"=== ERROR IN MAIN: {e} ===\n")
        sys.stderr.flush()
        raise


if __name__ == "__main__":
    sys.stderr.write("=== __main__ BLOCK ENTERED ===\n")
    sys.stderr.flush()
    main()
