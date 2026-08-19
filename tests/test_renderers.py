import pytest

from weather_cli.models import CurrentWeather, Location, WeatherReport
from weather_cli.renderers import RichWeatherRenderer


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
