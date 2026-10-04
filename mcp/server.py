from typing import Any
import httpx2
import logging

from mcp.server import MCPServer

# Initialize MCPServer
mcp = MCPServer("weather")

logger = logging.getLogger(__name__)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(endpoint: str) -> dict[str, Any] | None:

    """
    Make a request to the NWS API with proper error handling.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(endpoint, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """
    Get weather alerts for a given US state.

    Args:
        state (str): The two-letter state code (e.g., 'CA' for California).
    """
    logger.info(f"Fetching weather alerts for state: {state}")

    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts available."

    if not data["features"]:
        return f"No active weather alerts for {state.upper()}."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_weather_forecast(lat: float, lon: float) -> str:
    """
    Get the weather forecast for a given latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    """
    logger.info(f"Fetching weather forecast for coordinates: {lat}, {lon}")

    url = f"{NWS_API_BASE}/points/{lat},{lon}"
    data = await make_nws_request(url)
    if not data or "properties" not in data or "forecast" not in data["properties"]:
        return "Unable to fetch forecast data."

    forecast_url = data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data or "properties" not in forecast_data or "periods" not in forecast_data["properties"]:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:10]:
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast.strip())
    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    mcp.run(transport="stdio")