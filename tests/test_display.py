from io import StringIO

from rich.console import Console

from weather_cli import display


def make_test_console():
    """Create an in-memory Rich console for output testing."""

    buffer = StringIO()

    console = Console(
        file=buffer,
        force_terminal=False,
        color_system=None,
        width=160,
    )

    return console, buffer


def test_north_wind():
    assert display.get_wind_direction(0) == "N"


def test_northeast_wind():
    assert display.get_wind_direction(45) == "NE"


def test_east_wind():
    assert display.get_wind_direction(90) == "E"


def test_southeast_wind():
    assert display.get_wind_direction(135) == "SE"


def test_south_wind():
    assert display.get_wind_direction(180) == "S"


def test_southwest_wind():
    assert display.get_wind_direction(225) == "SW"


def test_west_wind():
    assert display.get_wind_direction(270) == "W"


def test_northwest_wind():
    assert display.get_wind_direction(315) == "NW"


def test_wind_direction_wraps_around():
    assert display.get_wind_direction(360) == "N"


def test_format_location_with_state():
    location = {
        "name": "Atlanta",
        "state": "Georgia",
    }

    assert display.format_location(location) == "Atlanta, Georgia"


def test_format_location_without_state():
    location = {
        "name": "London",
        "state": "",
    }

    assert display.format_location(location) == "London"


def test_format_location_missing_state_key():
    location = {
        "name": "Tokyo",
    }

    assert display.format_location(location) == "Tokyo"


def test_imperial_units():
    assert display.get_units(False) == {
        "temperature": "°F",
        "wind": "mph",
        "precipitation": "in",
    }


def test_metric_units():
    assert display.get_units(True) == {
        "temperature": "°C",
        "wind": "km/h",
        "precipitation": "mm",
    }


def test_clear_weather_icon():
    assert display.get_weather_icon(0) == "☀"


def test_mainly_clear_weather_icon():
    assert display.get_weather_icon(1) == "⛅"


def test_partly_cloudy_weather_icon():
    assert display.get_weather_icon(2) == "⛅"


def test_overcast_weather_icon():
    assert display.get_weather_icon(3) == "☁"


def test_fog_weather_icon():
    assert display.get_weather_icon(45) == "🌫"


def test_rime_fog_weather_icon():
    assert display.get_weather_icon(48) == "🌫"


def test_drizzle_weather_icon():
    for code in (
        51,
        53,
        55,
        56,
        57,
    ):
        assert display.get_weather_icon(code) == "🌦"


def test_rain_weather_icon():
    for code in (
        61,
        63,
        65,
        66,
        67,
    ):
        assert display.get_weather_icon(code) == "🌧"


def test_snow_weather_icon():
    for code in (
        71,
        73,
        75,
        77,
        85,
        86,
    ):
        assert display.get_weather_icon(code) == "❄"


def test_rain_showers_weather_icon():
    for code in (
        80,
        81,
        82,
    ):
        assert display.get_weather_icon(code) == "🌦"


def test_thunderstorm_weather_icon():
    for code in (
        95,
        96,
        99,
    ):
        assert display.get_weather_icon(code) == "⛈"


def test_unknown_weather_icon():
    assert display.get_weather_icon(999) == "?"


def test_format_time_with_datetime():
    assert display.format_time("2026-08-18T06:45") == "06:45"


def test_format_time_without_date():
    assert display.format_time("06:45") == "06:45"


def test_format_time_empty_string():
    assert display.format_time("") == "-"


def test_format_time_none():
    assert display.format_time(None) == "-"


def test_display_current_weather_imperial(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    location = {
        "name": "Atlanta",
        "state": "Georgia",
        "country": "United States",
        "timezone": "America/New_York",
    }

    weather = {
        "current": {
            "weather_code": 2,
            "temperature_2m": 82.0,
            "apparent_temperature": 85.0,
            "relative_humidity_2m": 65,
            "precipitation": 0.1,
            "wind_speed_10m": 8.5,
            "wind_direction_10m": 225,
            "wind_gusts_10m": 14.0,
        }
    }

    display.display_current_weather(
        location,
        weather,
        False,
    )

    output = buffer.getvalue()
    normalized_output = output.replace("\n", "")

    assert "Atlanta, Georgia" in normalized_output
    assert "United States" in normalized_output

    # Rich may truncate the long subtitle depending on panel width.
    assert "America/New_Y" in normalized_output

    assert "Partly Cloudy" in output
    assert "82.0 °F" in output
    assert "85.0 °F" in output
    assert "65%" in output
    assert "0.1 in" in output
    assert "8.5 mph SW" in output
    assert "14.0 mph" in output


def test_display_current_weather_metric(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    location = {
        "name": "London",
        "state": "",
        "country": "United Kingdom",
        "timezone": "Europe/London",
    }

    weather = {
        "current": {
            "weather_code": 61,
            "temperature_2m": 18.5,
            "apparent_temperature": 17.9,
            "relative_humidity_2m": 78,
            "precipitation": 2.4,
            "wind_speed_10m": 16.0,
            "wind_direction_10m": 90,
            "wind_gusts_10m": 25.0,
        }
    }

    display.display_current_weather(
        location,
        weather,
        True,
    )

    output = buffer.getvalue()
    normalized_output = output.replace("\n", "")

    assert "London" in normalized_output
    assert "United Kingdom" in normalized_output
    assert "Europe/London" in normalized_output

    assert "Light Rain" in output
    assert "18.5 °C" in output
    assert "17.9 °C" in output
    assert "78%" in output
    assert "2.4 mm" in output
    assert "16.0 km/h E" in output
    assert "25.0 km/h" in output


def test_display_current_weather_without_optional_location_fields(
    monkeypatch,
):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    location = {
        "name": "Tokyo",
    }

    weather = {
        "current": {
            "weather_code": 0,
            "temperature_2m": 75.0,
            "apparent_temperature": 75.0,
            "relative_humidity_2m": 50,
            "precipitation": 0.0,
            "wind_speed_10m": 4.0,
            "wind_direction_10m": 0,
            "wind_gusts_10m": 6.0,
        }
    }

    display.display_current_weather(
        location,
        weather,
        False,
    )

    output = buffer.getvalue()

    assert "Tokyo" in output
    assert "Clear Sky" in output
    assert "75.0 °F" in output
    assert "50%" in output
    assert "4.0 mph N" in output


def test_display_forecast_imperial(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    weather = {
        "daily": {
            "time": [
                "2026-08-18",
                "2026-08-19",
            ],
            "weather_code": [
                0,
                61,
            ],
            "temperature_2m_max": [
                88.0,
                84.0,
            ],
            "temperature_2m_min": [
                70.0,
                69.0,
            ],
            "precipitation_probability_max": [
                10,
                70,
            ],
            "precipitation_sum": [
                0.0,
                0.25,
            ],
            "wind_speed_10m_max": [
                9.0,
                12.0,
            ],
            "sunrise": [
                "2026-08-18T06:58",
                "2026-08-19T06:59",
            ],
            "sunset": [
                "2026-08-18T20:17",
                "2026-08-19T20:16",
            ],
        }
    }

    display.display_forecast(
        weather,
        False,
    )

    output = buffer.getvalue()

    assert "Daily Forecast" in output

    assert "2026-08-18" in output
    assert "2026-08-19" in output

    assert "Clear Sky" in output
    assert "Light Rain" in output

    assert "88.0 °F" in output
    assert "70.0 °F" in output
    assert "84.0 °F" in output
    assert "69.0 °F" in output

    assert "10%" in output
    assert "70%" in output

    assert "0.0 in" in output
    assert "0.25 in" in output

    assert "9.0 mph" in output
    assert "12.0 mph" in output

    assert "06:58" in output
    assert "06:59" in output

    assert "20:17" in output
    assert "20:16" in output


def test_display_forecast_metric(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    weather = {
        "daily": {
            "time": [
                "2026-08-18",
            ],
            "weather_code": [
                3,
            ],
            "temperature_2m_max": [
                23.5,
            ],
            "temperature_2m_min": [
                14.0,
            ],
            "precipitation_probability_max": [
                40,
            ],
            "precipitation_sum": [
                3.2,
            ],
            "wind_speed_10m_max": [
                21.0,
            ],
            "sunrise": [
                "2026-08-18T05:45",
            ],
            "sunset": [
                "2026-08-18T20:10",
            ],
        }
    }

    display.display_forecast(
        weather,
        True,
    )

    output = buffer.getvalue()

    assert "Daily Forecast" in output
    assert "2026-08-18" in output
    assert "Overcast" in output

    assert "23.5 °C" in output
    assert "14.0 °C" in output

    assert "40%" in output
    assert "3.2 mm" in output
    assert "21.0 km/h" in output

    assert "05:45" in output
    assert "20:10" in output


def test_display_forecast_preserves_plain_times(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    weather = {
        "daily": {
            "time": [
                "2026-08-18",
            ],
            "weather_code": [
                2,
            ],
            "temperature_2m_max": [
                80.0,
            ],
            "temperature_2m_min": [
                60.0,
            ],
            "precipitation_probability_max": [
                25,
            ],
            "precipitation_sum": [
                0.0,
            ],
            "wind_speed_10m_max": [
                7.0,
            ],
            "sunrise": [
                "06:00",
            ],
            "sunset": [
                "20:00",
            ],
        }
    }

    display.display_forecast(
        weather,
        False,
    )

    output = buffer.getvalue()

    assert "06:00" in output
    assert "20:00" in output


def test_display_forecast_with_empty_times(monkeypatch):
    test_console, buffer = make_test_console()

    monkeypatch.setattr(
        display,
        "console",
        test_console,
    )

    weather = {
        "daily": {
            "time": [
                "2026-08-18",
            ],
            "weather_code": [
                0,
            ],
            "temperature_2m_max": [
                80.0,
            ],
            "temperature_2m_min": [
                60.0,
            ],
            "precipitation_probability_max": [
                0,
            ],
            "precipitation_sum": [
                0.0,
            ],
            "wind_speed_10m_max": [
                5.0,
            ],
            "sunrise": [
                "",
            ],
            "sunset": [
                None,
            ],
        }
    }

    display.display_forecast(
        weather,
        False,
    )

    output = buffer.getvalue()

    assert "Daily Forecast" in output
    assert "-" in output
