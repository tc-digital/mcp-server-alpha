"""Main MCP server implementation for Research Assistant."""
import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools.analyzer import analyze_data_tool
from .tools.calculator import calculate_tool
from .tools.search import web_search_tool
from .tools.summarizer import summarize_tool


class MCPServerAlpha:
    """Main MCP server class for Research Assistant."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("mcp-server-alpha-research")

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
                                "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', 'sqrt(16)')",
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
                            text=f"Summary: {result['summary']}\n\nOriginal length: {result['original_length']} chars\nSummary length: {result['summary_length']} chars\nCompression ratio: {result['compression_ratio']:.2%}",
                        )
                    ]

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
    server = MCPServerAlpha()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
