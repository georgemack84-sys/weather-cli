from unittest.mock import Mock, patch

import pytest

from weather_cli.api import (
    build_weather_cache_key,
    get_hourly_weather,
    get_weather,
    search_locations,
)


@patch("weather_cli.api.requests.get")
def test_search_locations(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "results": [
            {
                "name": "Atlanta",
                "latitude": 33.749,
                "longitude": -84.388,
                "country": "United States",
                "country_code": "US",
                "admin1": "Georgia",
                "admin2": "Fulton County",
                "timezone": "America/New_York",
                "population": 498715,
            }
        ]
    }

    mock_get.return_value = mock_response

    locations = search_locations("Atlanta")

    assert len(locations) == 1

    location = locations[0]

    assert location["name"] == "Atlanta"
    assert location["state"] == "Georgia"
    assert location["country"] == "United States"
    assert location["country_code"] == "US"
    assert location["latitude"] == 33.749
    assert location["longitude"] == -84.388
    assert location["timezone"] == "America/New_York"

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("weather_cli.api.requests.get")
def test_search_locations_multiple_results(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "results": [
            {
                "name": "Springfield",
                "latitude": 39.7817,
                "longitude": -89.6501,
                "country": "United States",
                "country_code": "US",
                "admin1": "Illinois",
                "timezone": "America/Chicago",
            },
            {
                "name": "Springfield",
                "latitude": 37.2089,
                "longitude": -93.2923,
                "country": "United States",
                "country_code": "US",
                "admin1": "Missouri",
                "timezone": "America/Chicago",
            },
        ]
    }

    mock_get.return_value = mock_response

    locations = search_locations("Springfield")

    assert len(locations) == 2
    assert locations[0]["state"] == "Illinois"
    assert locations[1]["state"] == "Missouri"


@patch("weather_cli.api.requests.get")
def test_search_locations_not_found(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {}

    mock_get.return_value = mock_response

    locations = search_locations("NotARealCity")

    assert locations == []


@patch("weather_cli.api.requests.get")
def test_search_locations_uses_requested_count(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {"results": []}

    mock_get.return_value = mock_response

    search_locations(
        "Atlanta",
        count=10,
    )

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["name"] == "Atlanta"
    assert kwargs["params"]["count"] == 10
    assert kwargs["timeout"] == 10


def test_build_weather_cache_key_imperial():
    key = build_weather_cache_key(
        33.749,
        -84.388,
        3,
        False,
    )

    assert key == ("weather_33.749_-84.388_3_imperial")


def test_build_weather_cache_key_metric():
    key = build_weather_cache_key(
        51.5072,
        -0.1276,
        5,
        True,
    )

    assert key == ("weather_51.5072_-0.1276_5_metric")


@patch("weather_cli.api.save_cache")
@patch("weather_cli.api.load_cache")
@patch("weather_cli.api.requests.get")
def test_get_weather_imperial(
    mock_get,
    mock_load_cache,
    mock_save_cache,
):
    mock_load_cache.return_value = None

    mock_response = Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 82.0,
            "weather_code": 2,
        }
    }

    mock_get.return_value = mock_response

    weather = get_weather(
        33.749,
        -84.388,
        3,
        False,
    )

    assert weather["current"]["temperature_2m"] == 82.0
    assert weather["current"]["weather_code"] == 2

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    params = kwargs["params"]

    assert params["temperature_unit"] == "fahrenheit"
    assert params["wind_speed_unit"] == "mph"
    assert params["precipitation_unit"] == "inch"
    assert params["forecast_days"] == 3
    assert params["timezone"] == "auto"
    assert kwargs["timeout"] == 10

    mock_response.raise_for_status.assert_called_once()

    mock_load_cache.assert_called_once_with("weather_33.749_-84.388_3_imperial")

    mock_save_cache.assert_called_once_with(
        "weather_33.749_-84.388_3_imperial",
        weather,
    )


@patch("weather_cli.api.save_cache")
@patch("weather_cli.api.load_cache")
@patch("weather_cli.api.requests.get")
def test_get_weather_metric(
    mock_get,
    mock_load_cache,
    mock_save_cache,
):
    mock_load_cache.return_value = None

    mock_response = Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 28.0,
            "weather_code": 1,
        }
    }

    mock_get.return_value = mock_response

    weather = get_weather(
        51.5072,
        -0.1276,
        5,
        True,
    )

    assert weather["current"]["temperature_2m"] == 28.0
    assert weather["current"]["weather_code"] == 1

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    params = kwargs["params"]

    assert params["temperature_unit"] == "celsius"
    assert params["wind_speed_unit"] == "kmh"
    assert params["precipitation_unit"] == "mm"
    assert params["forecast_days"] == 5
    assert params["timezone"] == "auto"

    mock_load_cache.assert_called_once_with("weather_51.5072_-0.1276_5_metric")

    mock_save_cache.assert_called_once_with(
        "weather_51.5072_-0.1276_5_metric",
        weather,
    )


@patch("weather_cli.api.save_cache")
@patch("weather_cli.api.load_cache")
@patch("weather_cli.api.requests.get")
def test_get_weather_cache_hit(
    mock_get,
    mock_load_cache,
    mock_save_cache,
):
    cached_weather = {
        "current": {
            "temperature_2m": 75.0,
            "weather_code": 0,
        }
    }

    mock_load_cache.return_value = cached_weather

    result = get_weather(
        33.749,
        -84.388,
        3,
        False,
    )

    assert result == cached_weather

    mock_get.assert_not_called()
    mock_save_cache.assert_not_called()


@patch("weather_cli.api.save_cache")
@patch("weather_cli.api.load_cache")
@patch("weather_cli.api.requests.get")
def test_cache_miss_calls_api_and_saves_result(
    mock_get,
    mock_load_cache,
    mock_save_cache,
):
    mock_load_cache.return_value = None

    api_data = {
        "current": {
            "temperature_2m": 70.0,
            "weather_code": 1,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = api_data

    mock_get.return_value = mock_response

    result = get_weather(
        40.0,
        -75.0,
        4,
        False,
    )

    assert result == api_data

    mock_get.assert_called_once()

    mock_save_cache.assert_called_once_with(
        "weather_40.0_-75.0_4_imperial",
        api_data,
    )


def make_hourly_api_response(hours: int = 3) -> dict:
    return {
        "hourly": {
            "time": [f"2026-08-19T{hour:02d}:00" for hour in range(hours)],
            "temperature_2m": [75.0 + hour for hour in range(hours)],
            "apparent_temperature": [76.0 + hour for hour in range(hours)],
            "relative_humidity_2m": [70 - hour for hour in range(hours)],
            "weather_code": [1 for _ in range(hours)],
            "precipitation_probability": [10 for _ in range(hours)],
            "precipitation": [0.0 for _ in range(hours)],
            "wind_speed_10m": [5.0 for _ in range(hours)],
            "wind_direction_10m": [180 for _ in range(hours)],
            "wind_gusts_10m": [8.0 for _ in range(hours)],
        }
    }


@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_imperial(mock_get):
    api_data = make_hourly_api_response(hours=24)

    mock_response = Mock()
    mock_response.json.return_value = api_data
    mock_get.return_value = mock_response

    result = get_hourly_weather(
        33.749,
        -84.388,
        24,
        False,
    )

    assert result == api_data

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    params = kwargs["params"]

    assert params["latitude"] == 33.749
    assert params["longitude"] == -84.388
    assert params["temperature_unit"] == "fahrenheit"
    assert params["wind_speed_unit"] == "mph"
    assert params["precipitation_unit"] == "inch"
    assert params["forecast_hours"] == 24
    assert params["timezone"] == "auto"
    assert kwargs["timeout"] == 10

    mock_response.raise_for_status.assert_called_once()


@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_metric(mock_get):
    api_data = make_hourly_api_response(hours=12)

    mock_response = Mock()
    mock_response.json.return_value = api_data
    mock_get.return_value = mock_response

    result = get_hourly_weather(
        51.5072,
        -0.1276,
        12,
        True,
    )

    assert result == api_data

    _, kwargs = mock_get.call_args
    params = kwargs["params"]

    assert params["temperature_unit"] == "celsius"
    assert params["wind_speed_unit"] == "kmh"
    assert params["precipitation_unit"] == "mm"
    assert params["forecast_hours"] == 12
    assert params["timezone"] == "auto"

    mock_response.raise_for_status.assert_called_once()


@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_requests_expected_variables(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = make_hourly_api_response(hours=6)
    mock_get.return_value = mock_response

    get_hourly_weather(
        33.749,
        -84.388,
        6,
        False,
    )

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["hourly"] == [
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "weather_code",
        "precipitation_probability",
        "precipitation",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
    ]


@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_preserves_raw_response(mock_get):
    api_data = {
        "latitude": 33.749,
        "longitude": -84.388,
        "timezone": "America/New_York",
        "hourly": {
            "time": ["2026-08-19T05:00"],
            "temperature_2m": [74.5],
        },
    }

    mock_response = Mock()
    mock_response.json.return_value = api_data
    mock_get.return_value = mock_response

    result = get_hourly_weather(
        33.749,
        -84.388,
        1,
        False,
    )

    assert result is api_data


@pytest.mark.parametrize("hours", [1, 48])
@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_accepts_boundary_hours(
    mock_get,
    hours,
):
    mock_response = Mock()
    mock_response.json.return_value = make_hourly_api_response(hours=1)
    mock_get.return_value = mock_response

    get_hourly_weather(
        33.749,
        -84.388,
        hours,
        False,
    )

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["forecast_hours"] == hours
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize("hours", [0, 49])
@patch("weather_cli.api.requests.get")
def test_get_hourly_weather_rejects_invalid_hours(
    mock_get,
    hours,
):
    with pytest.raises(
        ValueError,
        match="Hourly forecast hours must be between 1 and 48",
    ):
        get_hourly_weather(
            33.749,
            -84.388,
            hours,
            False,
        )

    mock_get.assert_not_called()
