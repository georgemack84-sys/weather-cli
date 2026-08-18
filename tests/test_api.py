from unittest.mock import Mock, patch

from weather_cli.api import (
    build_weather_cache_key,
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

    mock_response.json.return_value = {
        "results": []
    }

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

    assert key == (
        "weather_33.749_-84.388_3_imperial"
    )


def test_build_weather_cache_key_metric():
    key = build_weather_cache_key(
        51.5072,
        -0.1276,
        5,
        True,
    )

    assert key == (
        "weather_51.5072_-0.1276_5_metric"
    )


@patch("weather_cli.api.save_cache")
@patch("weather_cli.api.load_cache")
@patch("weather_cli.api.requests.get")
def test_get_weather_imperial(
    mock_get,
    mock_load_cache,
    mock_save_cache,
):
    # Force a cache miss so the HTTP request is exercised.
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

    mock_load_cache.assert_called_once_with(
        "weather_33.749_-84.388_3_imperial"
    )

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
    # Force a cache miss.
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

    mock_load_cache.assert_called_once_with(
        "weather_51.5072_-0.1276_5_metric"
    )

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

    # A cache hit should completely avoid the network.
    mock_get.assert_not_called()

    # We also should not rewrite an already valid cache entry.
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