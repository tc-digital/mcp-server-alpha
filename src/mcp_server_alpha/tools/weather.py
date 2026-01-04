"""Weather forecast tool using weather.gov API."""
import re
from typing import Any

import httpx


async def weather_forecast_tool(
    location: str, forecast_type: str = "forecast"
) -> dict[str, Any]:
    """
    Get weather forecast for a location using weather.gov API.

    Args:
        location: Location as zip code (e.g., "10001") or lat,lon (e.g., "39.7456,-97.0892")
        forecast_type: Type of forecast - "forecast" (12h periods), "hourly" or "current"

    Returns:
        Dictionary with weather forecast data
    """
    try:
        # Parse location - check if it's a zip code or coordinates
        if re.match(r"^\d{5}$", location.strip()):
            # It's a zip code - convert to coordinates
            lat, lon = await _zipcode_to_coords(location.strip())
        elif "," in location:
            # It's coordinates
            parts = location.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
        else:
            return {
                "error": "Location must be a 5-digit zip code or lat,lon coordinates",
                "success": False,
            }

        # Get grid point data from weather.gov
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get grid endpoint for the coordinates
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            points_response = await client.get(
                points_url,
                headers={"User-Agent": "(MCP Weather Tool, contact@example.com)"},
            )
            points_response.raise_for_status()
            points_data = points_response.json()

            # Extract forecast URL based on type
            properties = points_data.get("properties", {})
            if forecast_type == "hourly":
                forecast_url = properties.get("forecastHourly")
            else:
                forecast_url = properties.get("forecast")

            if not forecast_url:
                return {
                    "error": "Could not get forecast URL from weather.gov",
                    "success": False,
                }

            # Get the forecast
            forecast_response = await client.get(
                forecast_url,
                headers={"User-Agent": "(MCP Weather Tool, contact@example.com)"},
            )
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Extract and format the forecast periods
            periods = forecast_data.get("properties", {}).get("periods", [])
            formatted_periods = []

            for period in periods[:7]:  # Limit to first 7 periods
                formatted_periods.append(
                    {
                        "name": period.get("name"),
                        "temperature": period.get("temperature"),
                        "temperatureUnit": period.get("temperatureUnit"),
                        "windSpeed": period.get("windSpeed"),
                        "windDirection": period.get("windDirection"),
                        "shortForecast": period.get("shortForecast"),
                        "detailedForecast": period.get("detailedForecast"),
                    }
                )

            return {
                "success": True,
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "city": properties.get("relativeLocation", {})
                    .get("properties", {})
                    .get("city"),
                    "state": properties.get("relativeLocation", {})
                    .get("properties", {})
                    .get("state"),
                },
                "forecast_type": forecast_type,
                "periods": formatted_periods,
                "updated": forecast_data.get("properties", {}).get("updated"),
            }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"Weather API error: {e.response.status_code} - {e.response.text[:200]}",
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
        }
    except (ValueError, KeyError) as e:
        return {
            "success": False,
            "error": f"Data parsing error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
        }


async def _zipcode_to_coords(zipcode: str) -> tuple[float, float]:
    """
    Convert US zip code to latitude/longitude coordinates.

    Uses a free geocoding service to convert zip codes to coordinates.

    Args:
        zipcode: 5-digit US zip code

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If zip code cannot be geocoded
    """
    # Use zippopotam.us API for free zip code lookup (US only)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://api.zippopotam.us/us/{zipcode}")
        response.raise_for_status()
        data = response.json()

        # Extract coordinates from first place
        places = data.get("places", [])
        if not places:
            raise ValueError(f"Could not find coordinates for zip code {zipcode}")

        lat = float(places[0]["latitude"])
        lon = float(places[0]["longitude"])
        return lat, lon
