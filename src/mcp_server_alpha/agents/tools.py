"""Tool wrappers for LangChain agent integration."""
from typing import Any

from langchain_core.tools import tool

from ..tools import analyze_data_tool, calculate_tool, summarize_tool, web_search_tool


class ResearchTools:
    """
    Wrapper for research tools to make them compatible with LangChain agents.
    """

    def __init__(self):
        """Initialize research tools."""
        pass

    def get_tools(self) -> list:
        """Get list of LangChain-compatible tools."""

        @tool
        async def web_search(query: str, max_results: int = 5) -> str:
            """
            Search the web for information on a topic.

            Args:
                query: What to search for
                max_results: Maximum number of results (default: 5)

            Returns:
                Formatted search results with sources
            """
            results = await web_search_tool(query, max_results)

            if not results:
                return "No search results found."

            output = f"Search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. **{result['title']}**\n"
                output += f"   {result['snippet']}\n"
                output += f"   URL: {result['url']}\n"
                output += f"   Reliability: {result['reliability_score']:.1%}\n\n"

            return output

        @tool
        async def summarize_text(text: str, max_length: int = 200) -> str:
            """
            Summarize a piece of text.

            Args:
                text: Text to summarize
                max_length: Maximum length of summary (default: 200 chars)

            Returns:
                Summarized text with metadata
            """
            result = await summarize_tool(text, max_length)

            output = f"Summary: {result['summary']}\n\n"
            output += f"Original length: {result['original_length']} chars\n"
            output += f"Summary length: {result['summary_length']} chars\n"
            output += f"Compression: {result['compression_ratio']:.1%}"

            return output

        @tool
        async def calculate(expression: str) -> str:
            """
            Perform mathematical calculations.

            Args:
                expression: Mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")

            Returns:
                Calculation result
            """
            result = await calculate_tool(expression)

            if result["success"]:
                return f"Result: {result['result']}"
            else:
                return f"Error: {result['error']}"

        @tool
        async def analyze_data(data: list[Any], analysis_type: str = "statistical") -> str:
            """
            Analyze data and provide insights.

            Args:
                data: List of data to analyze (numbers, strings, etc.)
                analysis_type: Type of analysis (statistical, trend, pattern)

            Returns:
                Analysis results and insights
            """
            result = await analyze_data_tool(data, analysis_type)

            if "error" in result:
                return f"Error: {result['error']}"

            output = f"Analysis ({analysis_type}):\n\n"
            for insight in result["insights"]:
                output += f"• {insight}\n"

            return output

        return [web_search, summarize_text, calculate, analyze_data]
