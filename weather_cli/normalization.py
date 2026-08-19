"""Normalization of provider-specific weather responses.

This module converts Open-Meteo/geocoding dictionaries into the stable
weather domain models consumed by application and presentation layers.
"""

from weather_cli.models import CurrentWeather, Location, WeatherReport
from weather_cli.weather_codes import get_weather_description


def normalize_location(location: dict) -> Location:
    """Convert a geocoding result into a normalized location."""

    return Location(
        name=location["name"],
        state=location.get("state") or None,
        country=location.get("country", ""),
        latitude=float(location["latitude"]),
        longitude=float(location["longitude"]),
        timezone=location.get("timezone", ""),
    )


def normalize_current_weather(
    location: dict,
    weather: dict,
    metric: bool,
) -> WeatherReport:
    """Convert an Open-Meteo current-weather response into a WeatherReport."""

    current = weather["current"]
    weather_code = int(current["weather_code"])

    normalized_current = CurrentWeather(
        temperature=float(current["temperature_2m"]),
        apparent_temperature=float(current["apparent_temperature"]),
        humidity=int(current["relative_humidity_2m"]),
        weather=get_weather_description(weather_code),
        weather_code=weather_code,
        wind_speed=float(current["wind_speed_10m"]),
        wind_direction=float(current["wind_direction_10m"]),
        wind_gusts=float(current["wind_gusts_10m"]),
        precipitation=float(current["precipitation"]),
    )

    return WeatherReport(
        location=normalize_location(location),
        units="metric" if metric else "imperial",
        current=normalized_current,
    )
