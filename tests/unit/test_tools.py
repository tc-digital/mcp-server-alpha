"""Tests for research tools."""
import pytest

from mcp_server_alpha.tools import (
    analyze_data_tool,
    calculate_tool,
    summarize_tool,
    weather_forecast_tool,
    web_search_tool,
)


@pytest.mark.asyncio
async def test_web_search():
    """Test web search tool."""
    results = await web_search_tool("test query", max_results=3)

    assert len(results) == 3
    assert all("title" in r for r in results)
    assert all("url" in r for r in results)
    assert all("snippet" in r for r in results)


@pytest.mark.asyncio
async def test_summarize():
    """Test summarization tool."""
    text = "This is a long text that needs to be summarized. " * 50
    result = await summarize_tool(text, max_length=100)

    assert "summary" in result
    assert "original_length" in result
    assert result["original_length"] > result["summary_length"]


@pytest.mark.asyncio
async def test_calculate_success():
    """Test calculator with valid expression."""
    result = await calculate_tool("2 + 2")

    assert result["success"] is True
    assert result["result"] == 4


@pytest.mark.asyncio
async def test_calculate_error():
    """Test calculator with invalid expression."""
    result = await calculate_tool("invalid")

    assert result["success"] is False
    assert result["error"] is not None


@pytest.mark.asyncio
async def test_analyze_numeric_data():
    """Test data analysis with numeric data."""
    data = [10, 20, 30, 40, 50]
    result = await analyze_data_tool(data, "statistical")

    assert "insights" in result
    assert len(result["insights"]) > 0
    assert any("Mean" in insight for insight in result["insights"])


@pytest.mark.asyncio
async def test_analyze_empty_data():
    """Test data analysis with empty data."""
    result = await analyze_data_tool([], "statistical")

    assert "error" in result


@pytest.mark.asyncio
async def test_weather_forecast_with_coordinates():
    """Test weather forecast with lat,lon coordinates."""
    # Using coordinates for Kansas (central US)
    result = await weather_forecast_tool("39.7456,-97.0892", "forecast")

    # Should succeed with real API
    if result.get("success"):
        assert "location" in result
        assert "periods" in result
        assert len(result["periods"]) > 0
        # Check first period has expected fields
        first_period = result["periods"][0]
        assert "temperature" in first_period
        assert "shortForecast" in first_period
    else:
        # If it fails, it should have an error message
        assert "error" in result


@pytest.mark.asyncio
async def test_weather_forecast_invalid_location():
    """Test weather forecast with invalid location format."""
    result = await weather_forecast_tool("invalid", "forecast")

    assert result["success"] is False
    assert "error" in result
