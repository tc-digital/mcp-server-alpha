"""Tests for research tools."""
import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_server_alpha.tools import (
    analyze_data_tool,
    calculate_tool,
    send_email_tool,
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


@pytest.mark.asyncio
async def test_weather_forecast_invalid_coordinates():
    """Test weather forecast with malformed coordinates."""
    # Test with missing coordinate part
    result = await weather_forecast_tool("39.7456", "forecast")
    assert result["success"] is False
    assert "error" in result

    # Test with non-numeric coordinates
    result = await weather_forecast_tool("abc,def", "forecast")
    assert result["success"] is False
    assert "error" in result

    # Test with out of range coordinates
    result = await weather_forecast_tool("999,-999", "forecast")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_send_email_missing_webhook_url():
    """Test send_email tool when webhook URL is not configured."""
    # Ensure POWER_AUTOMATE_WEBHOOK_URL is not set
    with patch.dict(os.environ, {}, clear=True):
        result = await send_email_tool(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body content",
        )

        assert result["success"] is False
        assert "not configured" in result["error"]


@pytest.mark.asyncio
async def test_send_email_invalid_email():
    """Test send_email tool with invalid email addresses."""
    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": "https://example.com/webhook"}):
        # Test with missing @
        result = await send_email_tool(
            to_email="invalid-email",
            subject="Test Subject",
            body="Test body",
        )
        assert result["success"] is False
        assert "Invalid email format" in result["error"]

        # Test with empty email
        result = await send_email_tool(
            to_email="",
            subject="Test Subject",
            body="Test body",
        )
        assert result["success"] is False
        assert "Invalid email format" in result["error"]

        # Test with missing domain
        result = await send_email_tool(
            to_email="test@",
            subject="Test Subject",
            body="Test body",
        )
        assert result["success"] is False
        assert "Invalid email format" in result["error"]


@pytest.mark.asyncio
async def test_send_email_invalid_subject():
    """Test send_email tool with invalid subject."""
    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": "https://example.com/webhook"}):
        # Test with empty subject
        result = await send_email_tool(
            to_email="test@example.com",
            subject="",
            body="Test body",
        )
        assert result["success"] is False
        assert "subject cannot be empty" in result["error"]

        # Test with subject exceeding max length
        long_subject = "x" * 501
        result = await send_email_tool(
            to_email="test@example.com",
            subject=long_subject,
            body="Test body",
        )
        assert result["success"] is False
        assert "exceeds maximum length" in result["error"]


@pytest.mark.asyncio
async def test_send_email_invalid_body():
    """Test send_email tool with invalid body."""
    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": "https://example.com/webhook"}):
        # Test with empty body
        result = await send_email_tool(
            to_email="test@example.com",
            subject="Test Subject",
            body="",
        )
        assert result["success"] is False
        assert "body cannot be empty" in result["error"]

        # Test with body exceeding max length
        long_body = "x" * 50001
        result = await send_email_tool(
            to_email="test@example.com",
            subject="Test Subject",
            body=long_body,
        )
        assert result["success"] is False
        assert "exceeds maximum length" in result["error"]


@pytest.mark.asyncio
async def test_send_email_success():
    """Test send_email tool with valid inputs and successful webhook call."""
    webhook_url = "https://example.com/webhook"

    # Mock httpx.AsyncClient
    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": webhook_url}):
        with patch("mcp_server_alpha.tools.send_email.httpx.AsyncClient") as mock_client_class:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = AsyncMock()

            # Setup mock client
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await send_email_tool(
                to_email="test@example.com",
                subject="Test Subject",
                body="This is a test email body.",
            )

            assert result["success"] is True
            assert result["message"] == "Email sent successfully"
            assert result["to_email"] == "test@example.com"
            assert result["subject"] == "Test Subject"

            # Verify the webhook was called correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == webhook_url
            assert call_args[1]["json"]["to_email"] == "test@example.com"
            assert call_args[1]["json"]["subject"] == "Test Subject"
            assert call_args[1]["json"]["body"] == "This is a test email body."


@pytest.mark.asyncio
async def test_send_email_webhook_http_error():
    """Test send_email tool when webhook returns HTTP error."""
    webhook_url = "https://example.com/webhook"

    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": webhook_url}):
        with patch("mcp_server_alpha.tools.send_email.httpx.AsyncClient") as mock_client_class:
            # Setup mock response with error
            mock_response = AsyncMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"

            # Create a mock request
            mock_request = AsyncMock()

            # Setup mock to raise HTTPStatusError
            http_error = httpx.HTTPStatusError(
                "Bad Request",
                request=mock_request,
                response=mock_response
            )

            # Setup mock client
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=http_error)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await send_email_tool(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test body",
            )

            assert result["success"] is False
            assert "webhook error" in result["error"]
            assert "400" in result["error"]


@pytest.mark.asyncio
async def test_send_email_network_error():
    """Test send_email tool when network error occurs."""
    webhook_url = "https://example.com/webhook"

    with patch.dict(os.environ, {"POWER_AUTOMATE_WEBHOOK_URL": webhook_url}):
        with patch("mcp_server_alpha.tools.send_email.httpx.AsyncClient") as mock_client_class:
            # Setup mock to raise RequestError
            network_error = httpx.RequestError("Connection refused")

            # Setup mock client
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=network_error)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await send_email_tool(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test body",
            )

            assert result["success"] is False
            assert "Network error" in result["error"]
