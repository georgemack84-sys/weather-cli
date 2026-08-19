import json

import pytest

from weather_cli.models import (
    CurrentWeather,
    DailyForecast,
    Location,
    WeatherReport,
)
from weather_cli.renderers import JsonWeatherRenderer, RichWeatherRenderer


def make_report(*, units: str = "imperial") -> WeatherReport:
    return WeatherReport(
        location=Location(
            name="Atlanta",
            state="Georgia",
            country="United States",
            latitude=33.749,
            longitude=-84.388,
            timezone="America/New_York",
        ),
        units=units,
        current=CurrentWeather(
            temperature=72.8,
            apparent_temperature=78.9,
            humidity=91,
            weather="Overcast",
            weather_code=3,
            wind_speed=8.2,
            wind_direction=210.0,
            wind_gusts=12.4,
            precipitation=0.0,
        ),
    )


def make_forecast_report(*, units: str = "imperial") -> WeatherReport:
    return WeatherReport(
        location=Location(
            name="Atlanta",
            state="Georgia",
            country="United States",
            latitude=33.749,
            longitude=-84.388,
            timezone="America/New_York",
        ),
        units=units,
        current=CurrentWeather(
            temperature=74.0,
            apparent_temperature=79.5,
            humidity=84,
            weather="Mainly Clear",
            weather_code=1,
            wind_speed=4.7,
            wind_direction=267.0,
            wind_gusts=8.7,
            precipitation=0.0,
        ),
        forecast=(
            DailyForecast(
                date="2026-08-19",
                weather="Partly Cloudy",
                temperature_max=84.0,
                temperature_min=68.0,
                precipitation_probability=20,
                precipitation=0.01,
                wind_speed_max=12.4,
            ),
            DailyForecast(
                date="2026-08-20",
                weather="Slight Rain",
                temperature_max=80.0,
                temperature_min=66.0,
                precipitation_probability=70,
                precipitation=0.25,
                wind_speed_max=15.0,
            ),
        ),
    )


def test_rich_renderer_adapts_current_weather(monkeypatch) -> None:
    captured = {}

    def fake_display_current_weather(location, weather, metric):
        captured["location"] = location
        captured["weather"] = weather
        captured["metric"] = metric

    monkeypatch.setattr(
        "weather_cli.renderers.display_current_weather",
        fake_display_current_weather,
    )

    renderer = RichWeatherRenderer()
    renderer.render_current(make_report())

    assert captured["location"] == {
        "name": "Atlanta",
        "state": "Georgia",
        "country": "United States",
        "latitude": 33.749,
        "longitude": -84.388,
        "timezone": "America/New_York",
    }

    assert captured["weather"] == {
        "current": {
            "temperature_2m": 72.8,
            "apparent_temperature": 78.9,
            "relative_humidity_2m": 91,
            "weather_code": 3,
            "wind_speed_10m": 8.2,
            "wind_direction_10m": 210.0,
            "wind_gusts_10m": 12.4,
            "precipitation": 0.0,
        }
    }

    assert captured["metric"] is False


def test_rich_renderer_uses_metric_units(monkeypatch) -> None:
    captured = {}

    def fake_display_current_weather(location, weather, metric):
        captured["metric"] = metric

    monkeypatch.setattr(
        "weather_cli.renderers.display_current_weather",
        fake_display_current_weather,
    )

    renderer = RichWeatherRenderer()
    renderer.render_current(make_report(units="metric"))

    assert captured["metric"] is True


def test_rich_renderer_rejects_report_without_current_weather() -> None:
    report = WeatherReport(
        location=Location(
            name="Atlanta",
            state="Georgia",
            country="United States",
            latitude=33.749,
            longitude=-84.388,
            timezone="America/New_York",
        ),
        units="imperial",
    )

    renderer = RichWeatherRenderer()

    with pytest.raises(
        ValueError,
        match="WeatherReport does not contain current weather",
    ):
        renderer.render_current(report)


def test_rich_renderer_delegates_forecast(monkeypatch) -> None:
    captured = {}
    weather = {"daily": {"time": ["2026-08-19"]}}

    def fake_display_forecast(received_weather, metric):
        captured["weather"] = received_weather
        captured["metric"] = metric

    monkeypatch.setattr(
        "weather_cli.renderers.display_forecast",
        fake_display_forecast,
    )

    renderer = RichWeatherRenderer()
    renderer.render_forecast(weather, metric=True)

    assert captured["weather"] is weather
    assert captured["metric"] is True


def test_json_renderer_outputs_valid_current_weather_json(capsys) -> None:
    renderer = JsonWeatherRenderer()

    renderer.render_current(make_report())

    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload == {
        "schema_version": "1",
        "location": {
            "name": "Atlanta",
            "state": "Georgia",
            "country": "United States",
            "latitude": 33.749,
            "longitude": -84.388,
            "timezone": "America/New_York",
        },
        "units": "imperial",
        "current": {
            "temperature": 72.8,
            "feels_like": 78.9,
            "humidity": 91,
            "weather": "Overcast",
            "weather_code": 3,
            "wind_speed": 8.2,
            "wind_direction": 210.0,
            "wind_gusts": 12.4,
            "precipitation": 0.0,
        },
    }


def test_json_renderer_preserves_missing_state(capsys) -> None:
    report = WeatherReport(
        location=Location(
            name="London",
            state=None,
            country="United Kingdom",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="Europe/London",
        ),
        units="metric",
        current=CurrentWeather(
            temperature=20.0,
            apparent_temperature=19.0,
            humidity=60,
            weather="Clear Sky",
            weather_code=0,
        ),
    )

    renderer = JsonWeatherRenderer()
    renderer.render_current(report)

    payload = json.loads(capsys.readouterr().out)

    assert payload["location"]["state"] is None
    assert payload["units"] == "metric"


def test_json_renderer_rejects_report_without_current_weather() -> None:
    report = WeatherReport(
        location=Location(
            name="Atlanta",
            state="Georgia",
            country="United States",
            latitude=33.749,
            longitude=-84.388,
            timezone="America/New_York",
        ),
        units="imperial",
    )

    renderer = JsonWeatherRenderer()

    with pytest.raises(
        ValueError,
        match="WeatherReport does not contain current weather",
    ):
        renderer.render_current(report)


def test_json_renderer_outputs_forecast_json(capsys) -> None:
    renderer = JsonWeatherRenderer()

    renderer.render_forecast(make_forecast_report())

    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["schema_version"] == "1"
    assert payload["location"] == {
        "name": "Atlanta",
        "state": "Georgia",
        "country": "United States",
        "latitude": 33.749,
        "longitude": -84.388,
        "timezone": "America/New_York",
    }
    assert payload["units"] == "imperial"

    assert payload["current"] == {
        "temperature": 74.0,
        "feels_like": 79.5,
        "humidity": 84,
        "weather": "Mainly Clear",
        "weather_code": 1,
        "wind_speed": 4.7,
        "wind_direction": 267.0,
        "wind_gusts": 8.7,
        "precipitation": 0.0,
    }

    assert payload["forecast"] == [
        {
            "date": "2026-08-19",
            "weather": "Partly Cloudy",
            "temperature_max": 84.0,
            "temperature_min": 68.0,
            "precipitation_probability": 20,
            "precipitation": 0.01,
            "wind_speed_max": 12.4,
        },
        {
            "date": "2026-08-20",
            "weather": "Slight Rain",
            "temperature_max": 80.0,
            "temperature_min": 66.0,
            "precipitation_probability": 70,
            "precipitation": 0.25,
            "wind_speed_max": 15.0,
        },
    ]


def test_json_renderer_forecast_without_items_omits_forecast(capsys) -> None:
    renderer = JsonWeatherRenderer()

    renderer.render_forecast(make_report())

    payload = json.loads(capsys.readouterr().out)

    assert "forecast" not in payload
