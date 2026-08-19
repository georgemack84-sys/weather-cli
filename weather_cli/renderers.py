"""Output renderer boundary for normalized weather reports.

Renderers consume normalized domain models rather than provider-specific
API responses. Rich output targets human terminal use, while JSON output
provides a stable machine-readable interface for automation.
"""

from __future__ import annotations

import json
from typing import Protocol

from weather_cli.display import display_current_weather, display_forecast
from weather_cli.models import WeatherReport


class WeatherRenderer(Protocol):
    """Contract implemented by weather output renderers."""

    def render_current(self, report: WeatherReport) -> None:
        """Render normalized current-weather data."""

    def render_forecast(self, weather: dict, metric: bool) -> None:
        """Render forecast data during the transitional architecture."""


class RichWeatherRenderer:
    """Render weather information using the existing Rich presentation layer."""

    def render_current(self, report: WeatherReport) -> None:
        """Render normalized current weather using the legacy Rich display."""

        current = report.current

        if current is None:
            raise ValueError("WeatherReport does not contain current weather")

        location = {
            "name": report.location.name,
            "state": report.location.state or "",
            "country": report.location.country,
            "latitude": report.location.latitude,
            "longitude": report.location.longitude,
            "timezone": report.location.timezone,
        }

        weather = {
            "current": {
                "temperature_2m": current.temperature,
                "apparent_temperature": current.apparent_temperature,
                "relative_humidity_2m": current.humidity,
                "weather_code": current.weather_code,
                "wind_speed_10m": current.wind_speed,
                "wind_direction_10m": current.wind_direction,
                "wind_gusts_10m": current.wind_gusts,
                "precipitation": current.precipitation,
            }
        }

        display_current_weather(
            location,
            weather,
            metric=report.units == "metric",
        )

    def render_forecast(self, weather: dict, metric: bool) -> None:
        """Render forecast data using the established Rich table."""

        display_forecast(weather, metric)


class JsonWeatherRenderer:
    """Render normalized weather information as machine-readable JSON."""

    def render_current(self, report: WeatherReport) -> None:
        """Write normalized current-weather data as JSON."""

        current = report.current

        if current is None:
            raise ValueError("WeatherReport does not contain current weather")

        payload = {
            "schema_version": "1",
            "location": {
                "name": report.location.name,
                "state": report.location.state,
                "country": report.location.country,
                "latitude": report.location.latitude,
                "longitude": report.location.longitude,
                "timezone": report.location.timezone,
            },
            "units": report.units,
            "current": {
                "temperature": current.temperature,
                "feels_like": current.apparent_temperature,
                "humidity": current.humidity,
                "weather": current.weather,
                "weather_code": current.weather_code,
                "wind_speed": current.wind_speed,
                "wind_direction": current.wind_direction,
                "wind_gusts": current.wind_gusts,
                "precipitation": current.precipitation,
            },
        }

        print(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    def render_forecast(self, weather: dict, metric: bool) -> None:
        """JSON forecast output is introduced in GP-06."""

        raise NotImplementedError("JSON forecast output is not implemented yet")


rich_renderer = RichWeatherRenderer()
json_renderer = JsonWeatherRenderer()
