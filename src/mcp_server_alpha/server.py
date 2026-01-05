"""Main MCP server implementation for Research Assistant."""
import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .agents.reasoning_orchestrator import ReasoningOrchestrator
from .tools.analyzer import analyze_data_tool
from .tools.calculator import calculate_tool
from .tools.search import web_search_tool
from .tools.send_email import send_email_tool
from .tools.summarizer import summarize_tool
from .tools.weather import weather_forecast_tool

sys.stderr.write("=== ALL IMPORTS SUCCESSFUL ===\n")
sys.stderr.flush()

class MCPServerAlpha:
    """Main MCP server class for Research Assistant."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("mcp-server-alpha-research")

        # Initialize reasoning orchestrator (lazy initialization to avoid
        # API key requirements at startup)
        self._orchestrator = None

        # Register MCP tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available research tools."""
            return [
                Tool(
                    name="web_search",
                    description="Search the web for information on a given query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="calculate",
                    description="Perform mathematical calculations and evaluate expressions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": (
                                    "Mathematical expression to evaluate "
                                    "(e.g., '2 + 2', '10 * 5', 'sqrt(16)')"
                                ),
                            }
                        },
                        "required": ["expression"],
                    },
                ),
                Tool(
                    name="analyze_data",
                    description="Analyze numerical data and provide statistical insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Array of numerical values to analyze",
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["statistical", "trends", "patterns"],
                                "description": "Type of analysis to perform",
                                "default": "statistical",
                            },
                        },
                        "required": ["data"],
                    },
                ),
                Tool(
                    name="summarize_text",
                    description="Summarize long text into key points",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to summarize",
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum length of summary in words",
                                "default": 100,
                            },
                        },
                        "required": ["text"],
                    },
                ),
                Tool(
                    name="weather_forecast",
                    description=(
                        "Get weather forecast for a location using weather.gov API. "
                        "Supports US locations only."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": (
                                    "Location as 5-digit US zip code (e.g., '10001') or "
                                    "latitude,longitude (e.g., '39.7456,-97.0892')"
                                ),
                            },
                            "forecast_type": {
                                "type": "string",
                                "enum": ["forecast", "hourly"],
                                "description": (
                                    "Type of forecast: 'forecast' for 12-hour periods "
                                    "(default), 'hourly' for hourly forecast"
                                ),
                                "default": "forecast",
                            },
                        },
                        "required": ["location"],
                    },
                ),
                Tool(
                    name="send_email",
                    description=(
                        "Send an email by triggering a Power Automate flow via HTTP POST webhook. "
                        "Requires POWER_AUTOMATE_WEBHOOK_URL environment variable to be configured."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to_email": {
                                "type": "string",
                                "description": (
                                    "Recipient's email address "
                                    "(required, must be valid email format)"
                                ),
                            },
                            "subject": {
                                "type": "string",
                                "description": (
                                    "Email subject (required, max 500 characters)"
                                ),
                            },
                            "body": {
                                "type": "string",
                                "description": (
                                    "Email body content (required, max 50,000 characters)"
                                ),
                            },
                        },
                        "required": ["to_email", "subject", "body"],
                    },
                ),
                Tool(
                    name="reasoning_agent",
                    description=(
                        "Execute complex multi-step tasks using an autonomous reasoning agent "
                        "powered by LangGraph. The agent analyzes your goal, plans a sequence "
                        "of actions, orchestrates other MCP tools, and provides step-by-step "
                        "progress updates with visible reasoning. Use this for tasks requiring "
                        "multiple tools or complex decision-making. Requires OPENAI_API_KEY "
                        "environment variable."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "goal": {
                                "type": "string",
                                "description": (
                                    "Natural language description of the goal to achieve. "
                                    "Be specific about what you want the agent to do. "
                                    "Example: 'Research renewable energy trends, analyze the data, "
                                    "and calculate the growth rate over the last 5 years.'"
                                ),
                            },
                            "context": {
                                "type": "object",
                                "description": (
                                    "Optional context from previous agent executions to maintain "
                                    "continuity across related tasks."
                                ),
                            },
                        },
                        "required": ["goal"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "web_search":
                    result = await web_search_tool(
                        query=arguments["query"],
                        max_results=arguments.get("max_results", 5),
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "calculate":
                    result = await calculate_tool(expression=arguments["expression"])
                    return [
                        TextContent(
                            type="text",
                            text=f"Result: {result['result']}\nExpression: {result['expression']}",
                        )
                    ]

                elif name == "analyze_data":
                    result = await analyze_data_tool(
                        data=arguments["data"],
                        analysis_type=arguments.get("analysis_type", "statistical"),
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "summarize_text":
                    result = await summarize_tool(
                        text=arguments["text"],
                        max_length=arguments.get("max_length", 100),
                    )
                    return [
                        TextContent(
                            type="text",
                            text=(
                                f"Summary: {result['summary']}\n\n"
                                f"Original length: {result['original_length']} chars\n"
                                f"Summary length: {result['summary_length']} chars\n"
                                f"Compression ratio: {result['compression_ratio']:.2%}"
                            ),
                        )
                    ]

                elif name == "weather_forecast":
                    result = await weather_forecast_tool(
                        location=arguments["location"],
                        forecast_type=arguments.get("forecast_type", "forecast"),
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "send_email":
                    result = await send_email_tool(
                        to_email=arguments["to_email"],
                        subject=arguments["subject"],
                        body=arguments["body"],
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "reasoning_agent":
                    # Lazy initialization of orchestrator
                    if self._orchestrator is None:
                        try:
                            self._orchestrator = ReasoningOrchestrator()
                        except ValueError as e:
                            return [
                                TextContent(
                                    type="text",
                                    text=json.dumps(
                                        {
                                            "success": False,
                                            "error": str(e),
                                            "message": (
                                                "Reasoning agent requires OPENAI_API_KEY "
                                                "environment variable to be set."
                                            ),
                                        },
                                        indent=2,
                                    ),
                                )
                            ]

                    # Execute the goal using reasoning orchestrator
                    result = await self._orchestrator.execute(
                        goal=arguments["goal"],
                        context=arguments.get("context"),
                    )

                    # Format result for MCP response
                    formatted_result = {
                        "success": True,
                        "result": result["result"],
                        "execution_summary": {
                            "total_steps": len(result["steps"]),
                            "tools_used": [
                                tc.get("tool", "unknown")
                                for tc in result["tool_calls"]
                            ],
                            "tool_count": len(result["tool_calls"]),
                        },
                        "steps": result["steps"],
                        "tool_calls": result["tool_calls"],
                        "reasoning_chain": result["reasoning"],
                    }

                    return [TextContent(type="text", text=json.dumps(formatted_result, indent=2))]

                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            init_options = self.server.create_initialization_options()
            await self.server.run(read_stream, write_stream, init_options)


def main() -> None:
    """Entry point for the MCP server."""
    sys.stderr.write("=== MAIN FUNCTION CALLED ===\n")
    sys.stderr.flush()

    try:
        server = MCPServerAlpha()
        sys.stderr.write("=== SERVER INSTANCE CREATED ===\n")
        sys.stderr.flush()

        asyncio.run(server.run())
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
