from weather_cli.display import (
    format_location,
    get_units,
    get_wind_direction,
)


def test_north_wind():
    assert get_wind_direction(0) == "N"


def test_east_wind():
    assert get_wind_direction(90) == "E"


def test_south_wind():
    assert get_wind_direction(180) == "S"


def test_west_wind():
    assert get_wind_direction(270) == "W"


def test_northwest_wind():
    assert get_wind_direction(315) == "NW"


def test_format_location_with_state():
    location = {
        "name": "Atlanta",
        "state": "Georgia",
    }

    assert format_location(location) == "Atlanta, Georgia"


def test_format_location_without_state():
    location = {
        "name": "London",
        "state": "",
    }

    assert format_location(location) == "London"


def test_imperial_units():
    units = get_units(False)

    assert units["temperature"] == "°F"
    assert units["wind"] == "mph"
    assert units["precipitation"] == "in"


def test_metric_units():
    units = get_units(True)

    assert units["temperature"] == "°C"
    assert units["wind"] == "km/h"
    assert units["precipitation"] == "mm"