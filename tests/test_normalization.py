from weather_cli.models import CurrentWeather, Location, WeatherReport
from weather_cli.normalization import normalize_current_weather, normalize_location


def test_normalize_location() -> None:
    source = {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "country": "United States",
        "state": "Georgia",
        "timezone": "America/New_York",
    }

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
    location = {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "country": "United States",
        "state": "Georgia",
        "timezone": "America/New_York",
    }

    weather = {
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

    result = normalize_current_weather(
        location=location,
        weather=weather,
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
    location = {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "country": "United States",
        "state": "Georgia",
        "timezone": "America/New_York",
    }

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
        location=location,
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
