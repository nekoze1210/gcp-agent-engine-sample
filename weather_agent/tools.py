"""Weather search tools for the ADK weather agent."""

import json
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


def get_weather(city: str) -> dict[str, str]:
    """Retrieves the current weather report for a specified city.

    Uses the Open-Meteo Geocoding and Weather APIs (free, no API key required).

    Args:
        city: The name of the city for which to retrieve the weather report.

    Returns:
        dict: A dictionary containing the status and weather report or error message.
    """
    try:
        location = _geocode(city)
        if location is None:
            return {"status": "error", "error_message": f"City '{city}' not found."}

        lat, lon, location_name, country = location

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&timezone=auto"
        )
        with urlopen(weather_url, timeout=10) as response:
            weather_data: dict[str, Any] = json.loads(response.read().decode())

        current: dict[str, Any] = weather_data["current"]
        temperature: float = current["temperature_2m"]
        humidity: float = current["relative_humidity_2m"]
        wind_speed: float = current["wind_speed_10m"]
        weather_code: int = current["weather_code"]

        description = _weather_code_to_description(weather_code)

        return {
            "status": "success",
            "report": (
                f"{location_name} ({country}) の現在の天気:\n"
                f"- 天気: {description}\n"
                f"- 気温: {temperature}°C\n"
                f"- 湿度: {humidity}%\n"
                f"- 風速: {wind_speed} km/h"
            ),
        }
    except (URLError, KeyError, json.JSONDecodeError) as e:
        return {"status": "error", "error_message": f"Failed to fetch weather data: {e}"}


def get_weather_forecast(city: str, days: int = 7) -> dict[str, str]:
    """Retrieves the weather forecast for a specified city.

    Returns daily forecast including max/min temperature and weather conditions.
    Supports up to 16 days ahead.

    Args:
        city: The name of the city for which to retrieve the forecast.
        days: Number of forecast days (1-16). Defaults to 7.

    Returns:
        dict: A dictionary containing the status and forecast report or error message.
    """
    try:
        location = _geocode(city)
        if location is None:
            return {"status": "error", "error_message": f"City '{city}' not found."}

        lat, lon, location_name, country = location
        forecast_days = max(1, min(days, 16))

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code,"
            f"precipitation_probability_max,wind_speed_10m_max"
            f"&forecast_days={forecast_days}"
            f"&timezone=auto"
        )
        with urlopen(weather_url, timeout=10) as response:
            weather_data: dict[str, Any] = json.loads(response.read().decode())

        daily: dict[str, Any] = weather_data["daily"]
        dates: list[str] = daily["time"]
        max_temps: list[float] = daily["temperature_2m_max"]
        min_temps: list[float] = daily["temperature_2m_min"]
        codes: list[int] = daily["weather_code"]
        precip_probs: list[float] = daily["precipitation_probability_max"]
        wind_speeds: list[float] = daily["wind_speed_10m_max"]

        lines: list[str] = [f"{location_name} ({country}) の{forecast_days}日間の天気予報:\n"]
        for i, date in enumerate(dates):
            desc = _weather_code_to_description(codes[i])
            lines.append(
                f"  {date}: {desc} "
                f"(最高 {max_temps[i]}°C / 最低 {min_temps[i]}°C, "
                f"降水確率 {precip_probs[i]:.0f}%, "
                f"最大風速 {wind_speeds[i]} km/h)"
            )

        return {"status": "success", "report": "\n".join(lines)}
    except (URLError, KeyError, json.JSONDecodeError) as e:
        return {"status": "error", "error_message": f"Failed to fetch forecast data: {e}"}


def _geocode(city: str) -> tuple[float, float, str, str] | None:
    """Geocode a city name to coordinates using Open-Meteo API.

    Returns:
        A tuple of (latitude, longitude, name, country) or None if not found.
    """
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ja"
    )
    with urlopen(geo_url, timeout=10) as response:
        geo_data: dict[str, Any] = json.loads(response.read().decode())

    results: list[dict[str, Any]] = geo_data.get("results", [])
    if not results:
        return None

    loc = results[0]
    return (loc["latitude"], loc["longitude"], loc.get("name", city), loc.get("country", ""))


_WEATHER_CODES: dict[int, str] = {
    0: "快晴",
    1: "晴れ",
    2: "一部曇り",
    3: "曇り",
    45: "霧",
    48: "着氷性の霧",
    51: "弱い霧雨",
    53: "霧雨",
    55: "強い霧雨",
    61: "弱い雨",
    63: "雨",
    65: "強い雨",
    71: "弱い雪",
    73: "雪",
    75: "強い雪",
    80: "弱いにわか雨",
    81: "にわか雨",
    82: "激しいにわか雨",
    95: "雷雨",
    96: "雹を伴う雷雨",
    99: "激しい雹を伴う雷雨",
}


def _weather_code_to_description(code: int) -> str:
    """Convert WMO weather code to a human-readable Japanese description."""
    return _WEATHER_CODES.get(code, f"不明 (code: {code})")
