from dataclasses import FrozenInstanceError

import pytest

from weather_cli.models import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    Location,
    WeatherReport,
)


def test_location_stores_resolved_location_data() -> None:
    location = Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )

    assert location.name == "Atlanta"
    assert location.state == "Georgia"
    assert location.country == "United States"
    assert location.latitude == 33.749
    assert location.longitude == -84.388
    assert location.timezone == "America/New_York"


def test_location_allows_missing_state() -> None:
    location = Location(
        name="London",
        state=None,
        country="United Kingdom",
        latitude=51.5074,
        longitude=-0.1278,
        timezone="Europe/London",
    )

    assert location.state is None


def test_current_weather_stores_normalized_values() -> None:
    current = CurrentWeather(
        temperature=72.8,
        apparent_temperature=78.9,
        humidity=91,
        weather="Overcast",
        weather_code=3,
        wind_speed=8.2,
        wind_direction=210.0,
        wind_gusts=12.4,
        precipitation=0.0,
    )

    assert current.temperature == 72.8
    assert current.apparent_temperature == 78.9
    assert current.humidity == 91
    assert current.weather == "Overcast"
    assert current.weather_code == 3
    assert current.wind_speed == 8.2
    assert current.wind_direction == 210.0
    assert current.wind_gusts == 12.4
    assert current.precipitation == 0.0


def test_current_weather_optional_values_default_to_none() -> None:
    current = CurrentWeather(
        temperature=72.8,
        apparent_temperature=78.9,
        humidity=91,
        weather="Overcast",
        weather_code=3,
    )

    assert current.wind_speed is None
    assert current.wind_direction is None
    assert current.wind_gusts is None
    assert current.precipitation is None


def test_daily_forecast_stores_normalized_values() -> None:
    forecast = DailyForecast(
        date="2026-08-19",
        weather="Partly cloudy",
        temperature_max=84.0,
        temperature_min=68.0,
        precipitation_probability=30,
        precipitation=0.1,
        wind_speed_max=12.0,
    )

    assert forecast.date == "2026-08-19"
    assert forecast.weather == "Partly cloudy"
    assert forecast.temperature_max == 84.0
    assert forecast.temperature_min == 68.0
    assert forecast.precipitation_probability == 30
    assert forecast.precipitation == 0.1
    assert forecast.wind_speed_max == 12.0


def test_daily_forecast_optional_values_default_to_none() -> None:
    forecast = DailyForecast(
        date="2026-08-19",
        weather="Clear",
        temperature_max=84.0,
        temperature_min=68.0,
    )

    assert forecast.precipitation_probability is None
    assert forecast.precipitation is None
    assert forecast.wind_speed_max is None


def test_hourly_forecast_stores_normalized_values() -> None:
    forecast = HourlyForecast(
        time="2026-08-19T12:00",
        temperature=80.0,
        apparent_temperature=84.0,
        humidity=70,
        weather="Partly cloudy",
        precipitation_probability=20,
        precipitation=0.0,
        wind_speed=7.0,
    )

    assert forecast.time == "2026-08-19T12:00"
    assert forecast.temperature == 80.0
    assert forecast.apparent_temperature == 84.0
    assert forecast.humidity == 70
    assert forecast.weather == "Partly cloudy"
    assert forecast.precipitation_probability == 20
    assert forecast.precipitation == 0.0
    assert forecast.wind_speed == 7.0


def test_hourly_forecast_allows_missing_precipitation_probability() -> None:
    forecast = HourlyForecast(
        time="2026-08-19T12:00",
        temperature=80.0,
        apparent_temperature=84.0,
        humidity=70,
        weather="Clear",
        precipitation_probability=None,
        precipitation=0.0,
        wind_speed=7.0,
    )

    assert forecast.precipitation_probability is None


def test_weather_report_supports_current_weather() -> None:
    location = Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )

    current = CurrentWeather(
        temperature=72.8,
        apparent_temperature=78.9,
        humidity=91,
        weather="Overcast",
        weather_code=3,
    )

    report = WeatherReport(
        location=location,
        units="imperial",
        current=current,
    )

    assert report.location == location
    assert report.units == "imperial"
    assert report.current == current
    assert report.forecast == ()
    assert report.hourly == ()


def test_weather_report_supports_daily_forecast() -> None:
    location = Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )

    forecast = DailyForecast(
        date="2026-08-19",
        weather="Clear",
        temperature_max=84.0,
        temperature_min=68.0,
    )

    report = WeatherReport(
        location=location,
        units="imperial",
        forecast=(forecast,),
    )

    assert report.forecast == (forecast,)


def test_weather_report_supports_hourly_forecast() -> None:
    location = Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )

    hourly = HourlyForecast(
        time="2026-08-19T12:00",
        temperature=80.0,
        apparent_temperature=84.0,
        humidity=70,
        weather="Clear",
        precipitation_probability=10,
        precipitation=0.0,
        wind_speed=7.0,
    )

    report = WeatherReport(
        location=location,
        units="imperial",
        hourly=(hourly,),
    )

    assert report.hourly == (hourly,)


def test_models_are_immutable() -> None:
    location = Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )

    with pytest.raises(FrozenInstanceError):
        location.name = "Charlotte"  # type: ignore[misc]
