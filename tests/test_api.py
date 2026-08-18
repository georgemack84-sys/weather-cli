from unittest.mock import Mock, patch

from weather_cli.api import get_weather, search_locations


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

    search_locations("Atlanta", count=10)

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["name"] == "Atlanta"
    assert kwargs["params"]["count"] == 10
    assert kwargs["timeout"] == 10


@patch("weather_cli.api.requests.get")
def test_get_weather_imperial(mock_get):
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

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["temperature_unit"] == "fahrenheit"
    assert kwargs["params"]["wind_speed_unit"] == "mph"
    assert kwargs["params"]["precipitation_unit"] == "inch"
    assert kwargs["params"]["forecast_days"] == 3

    mock_response.raise_for_status.assert_called_once()


@patch("weather_cli.api.requests.get")
def test_get_weather_metric(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 28.0,
            "weather_code": 1,
        }
    }

    mock_get.return_value = mock_response

    get_weather(
        51.5072,
        -0.1276,
        5,
        True,
    )

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["temperature_unit"] == "celsius"
    assert kwargs["params"]["wind_speed_unit"] == "kmh"
    assert kwargs["params"]["precipitation_unit"] == "mm"
    assert kwargs["params"]["forecast_days"] == 5