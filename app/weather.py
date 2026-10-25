import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherError(Exception):
    """Raised when weather data cannot be fetched or parsed."""


def parse_weather(data):
    """Extract the fields we need from an OpenWeatherMap response."""
    try:
        return {
            "city": data["name"],
            "temperature_c": float(data["main"]["temp"]),
            "description": data["weather"][0]["description"],
        }
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WeatherError(f"Unexpected weather response: {exc}") from exc


def fetch_weather(city, api_key, timeout=10):
    """Fetch current weather for a city (metric units)."""
    if not api_key:
        raise WeatherError("WEATHER_API_KEY is not configured")
    try:
        resp = requests.get(
            API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise WeatherError(f"Weather API request failed: {exc}") from exc

    if resp.status_code != 200:
        raise WeatherError(f"Weather API returned status {resp.status_code}")
    try:
        return parse_weather(resp.json())
    except ValueError as exc:  # invalid JSON
        raise WeatherError("Weather API returned invalid JSON") from exc
