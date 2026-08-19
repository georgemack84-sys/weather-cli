from weather_cli.models import (
    CurrentWeather,
    DailyForecast,
    Location,
    WeatherReport,
)
from weather_cli.normalization import (
    normalize_current_weather,
    normalize_daily_forecast,
    normalize_location,
    normalize_weather_report,
)


def make_location() -> dict:
    return {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "country": "United States",
        "state": "Georgia",
        "timezone": "America/New_York",
    }


def make_current_weather() -> dict:
    return {
        "current": {
            "temperature_2m": 72.8,
            "apparent_temperature": 78.9,
            "relative_humidity_2m": 91,
            "weather_code": 3,
            "wind_speed_10m": 8.2,
            "wind_direction_10m": 210,
            "wind_gusts_10m": 12.4,
            "precipitation": 0.0,
        }
    }


def make_weather_with_forecast() -> dict:
    weather = make_current_weather()
    weather["daily"] = {
        "time": [
            "2026-08-19",
            "2026-08-20",
        ],
        "weather_code": [
            2,
            61,
        ],
        "temperature_2m_max": [
            84,
            80.5,
        ],
        "temperature_2m_min": [
            68,
            66.25,
        ],
        "precipitation_probability_max": [
            20,
            None,
        ],
        "precipitation_sum": [
            0.01,
            None,
        ],
        "wind_speed_10m_max": [
            12.4,
            None,
        ],
    }
    return weather


def test_normalize_location() -> None:
    source = make_location()

    result = normalize_location(source)

    assert result == Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )


def test_normalize_location_handles_missing_optional_values() -> None:
    source = {
        "name": "Example",
        "latitude": 10,
        "longitude": 20,
    }

    result = normalize_location(source)

    assert result == Location(
        name="Example",
        state=None,
        country="",
        latitude=10.0,
        longitude=20.0,
        timezone="",
    )


def test_normalize_current_weather_imperial() -> None:
    result = normalize_current_weather(
        location=make_location(),
        weather=make_current_weather(),
        metric=False,
    )

    assert result == WeatherReport(
        location=Location(
            name="Atlanta",
            state="Georgia",
            country="United States",
            latitude=33.749,
            longitude=-84.388,
            timezone="America/New_York",
        ),
        units="imperial",
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


def test_normalize_current_weather_metric() -> None:
    weather = {
        "current": {
            "temperature_2m": 22.7,
            "apparent_temperature": 24.2,
            "relative_humidity_2m": 70,
            "weather_code": 0,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 180,
            "wind_gusts_10m": 18.0,
            "precipitation": 0.0,
        }
    }

    result = normalize_current_weather(
        location=make_location(),
        weather=weather,
        metric=True,
    )

    assert result.units == "metric"
    assert result.current is not None
    assert result.current.temperature == 22.7
    assert result.current.apparent_temperature == 24.2
    assert result.current.humidity == 70
    assert result.current.weather == "Clear Sky"
    assert result.current.weather_code == 0
    assert result.current.wind_speed == 12.0
    assert result.current.wind_direction == 180.0
    assert result.current.wind_gusts == 18.0
    assert result.current.precipitation == 0.0


def test_normalize_daily_forecast() -> None:
    result = normalize_daily_forecast(make_weather_with_forecast())

    assert result == (
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
            weather="Light Rain",
            temperature_max=80.5,
            temperature_min=66.25,
            precipitation_probability=None,
            precipitation=None,
            wind_speed_max=None,
        ),
    )


def test_normalize_weather_report_without_forecast() -> None:
    weather = make_weather_with_forecast()

    result = normalize_weather_report(
        location=make_location(),
        weather=weather,
        metric=False,
        include_forecast=False,
    )

    assert result.location == Location(
        name="Atlanta",
        state="Georgia",
        country="United States",
        latitude=33.749,
        longitude=-84.388,
        timezone="America/New_York",
    )
    assert result.units == "imperial"
    assert result.current is not None
    assert result.current.weather == "Overcast"
    assert result.forecast == ()


def test_normalize_weather_report_with_forecast() -> None:
    weather = make_weather_with_forecast()

    result = normalize_weather_report(
        location=make_location(),
        weather=weather,
        metric=True,
        include_forecast=True,
    )

    assert result.units == "metric"
    assert result.current is not None
    assert len(result.forecast) == 2
    assert result.forecast[0].date == "2026-08-19"
    assert result.forecast[0].weather == "Partly Cloudy"
    assert result.forecast[1].date == "2026-08-20"
    assert result.forecast[1].weather == "Light Rain"
    assert result.forecast[1].precipitation_probability is None
    assert result.forecast[1].precipitation is None
    assert result.forecast[1].wind_speed_max is None
