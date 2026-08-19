"""Normalization of provider-specific weather responses.

This module converts Open-Meteo/geocoding dictionaries into the stable
weather domain models consumed by application and presentation layers.
"""

from weather_cli.models import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    Location,
    WeatherReport,
)
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


def normalize_daily_forecast(
    weather: dict,
) -> tuple[DailyForecast, ...]:
    """Convert Open-Meteo daily forecast data into normalized models."""

    daily = weather["daily"]
    forecasts = []

    for index, date in enumerate(daily["time"]):
        weather_code = int(daily["weather_code"][index])
        precipitation_probability = daily["precipitation_probability_max"][index]
        precipitation = daily["precipitation_sum"][index]
        wind_speed_max = daily["wind_speed_10m_max"][index]

        forecasts.append(
            DailyForecast(
                date=date,
                weather=get_weather_description(weather_code),
                temperature_max=float(daily["temperature_2m_max"][index]),
                temperature_min=float(daily["temperature_2m_min"][index]),
                precipitation_probability=(
                    int(precipitation_probability)
                    if precipitation_probability is not None
                    else None
                ),
                precipitation=(
                    float(precipitation) if precipitation is not None else None
                ),
                wind_speed_max=(
                    float(wind_speed_max) if wind_speed_max is not None else None
                ),
            )
        )

    return tuple(forecasts)


def normalize_hourly_forecast(
    weather: dict,
) -> tuple[HourlyForecast, ...]:
    """Convert Open-Meteo hourly forecast data into normalized models."""

    hourly = weather["hourly"]
    forecasts = []

    for index, time in enumerate(hourly["time"]):
        weather_code = int(hourly["weather_code"][index])
        precipitation_probability = hourly["precipitation_probability"][index]

        forecasts.append(
            HourlyForecast(
                time=time,
                temperature=float(hourly["temperature_2m"][index]),
                apparent_temperature=float(hourly["apparent_temperature"][index]),
                humidity=int(hourly["relative_humidity_2m"][index]),
                weather=get_weather_description(weather_code),
                precipitation_probability=(
                    int(precipitation_probability)
                    if precipitation_probability is not None
                    else None
                ),
                precipitation=float(hourly["precipitation"][index]),
                wind_speed=float(hourly["wind_speed_10m"][index]),
            )
        )

    return tuple(forecasts)


def normalize_weather_report(
    location: dict,
    weather: dict,
    metric: bool,
    *,
    include_forecast: bool = False,
    include_hourly: bool = False,
) -> WeatherReport:
    """Convert provider data into a complete normalized WeatherReport."""

    current_report = normalize_current_weather(
        location=location,
        weather=weather,
        metric=metric,
    )

    forecast = normalize_daily_forecast(weather) if include_forecast else ()

    hourly = normalize_hourly_forecast(weather) if include_hourly else ()

    return WeatherReport(
        location=current_report.location,
        units=current_report.units,
        current=current_report.current,
        forecast=forecast,
        hourly=hourly,
    )
