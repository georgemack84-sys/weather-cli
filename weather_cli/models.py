"""Normalized weather domain models.

These models form the internal data contract between weather data providers
and output renderers. Provider-specific response structures should not leak
beyond the normalization boundary.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    """A resolved geographic location."""

    name: str
    state: str | None
    country: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True, slots=True)
class CurrentWeather:
    """Normalized current-weather observations."""

    temperature: float
    apparent_temperature: float
    humidity: int
    weather: str
    wind_speed: float | None = None
    wind_direction: float | None = None
    precipitation: float | None = None


@dataclass(frozen=True, slots=True)
class DailyForecast:
    """Normalized daily forecast data."""

    date: str
    weather: str
    temperature_max: float
    temperature_min: float
    precipitation_probability: int | None = None
    precipitation: float | None = None
    wind_speed_max: float | None = None


@dataclass(frozen=True, slots=True)
class HourlyForecast:
    """Normalized hourly forecast data."""

    time: str
    temperature: float
    apparent_temperature: float
    humidity: int
    weather: str
    precipitation_probability: int | None
    precipitation: float
    wind_speed: float


@dataclass(frozen=True, slots=True)
class WeatherReport:
    """Normalized weather response consumed by output renderers."""

    location: Location
    units: str
    current: CurrentWeather | None = None
    forecast: tuple[DailyForecast, ...] = ()
    hourly: tuple[HourlyForecast, ...] = ()
