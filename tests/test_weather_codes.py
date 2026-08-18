from weather_cli.weather_codes import get_weather_description


def test_clear_sky():
    assert get_weather_description(0) == "Clear Sky"


def test_partly_cloudy():
    assert get_weather_description(2) == "Partly Cloudy"


def test_thunderstorm():
    assert get_weather_description(95) == "Thunderstorm"


def test_unknown_weather_code():
    assert get_weather_description(999) == "Unknown (999)"