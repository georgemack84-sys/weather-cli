import pytest

import weather_cli.json_schema as json_schema


def make_payload() -> dict:
    """Return a valid Weather CLI schema-v1 current-weather payload."""

    return {
        "schema_version": json_schema.SCHEMA_VERSION,
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
            "temperature": 74.0,
            "feels_like": 79.5,
            "humidity": 84,
            "weather": "Mainly Clear",
            "weather_code": 1,
            "wind_speed": 4.7,
            "wind_direction": 267.0,
            "wind_gusts": 8.7,
            "precipitation": 0.0,
        },
    }


def make_forecast_item() -> dict:
    """Return a valid Weather CLI schema-v1 forecast item."""

    return {
        "date": "2026-08-19",
        "weather": "Overcast",
        "temperature_max": 93.6,
        "temperature_min": 69.9,
        "precipitation_probability": 2,
        "precipitation": 0.0,
        "wind_speed_max": 9.7,
    }


def test_schema_version_is_one() -> None:
    assert json_schema.SCHEMA_VERSION == "1"


def test_validate_current_payload() -> None:
    json_schema.validate_payload(make_payload())


def test_validate_forecast_payload() -> None:
    payload = make_payload()
    payload["forecast"] = [make_forecast_item()]

    json_schema.validate_payload(payload)


def test_rejects_unknown_schema_version() -> None:
    payload = make_payload()
    payload["schema_version"] = "2"

    with pytest.raises(
        ValueError,
        match="Unsupported schema version",
    ):
        json_schema.validate_payload(payload)


def test_rejects_invalid_units() -> None:
    payload = make_payload()
    payload["units"] = "kelvin"

    with pytest.raises(
        ValueError,
        match="Invalid units value",
    ):
        json_schema.validate_payload(payload)


def test_rejects_non_object_location() -> None:
    payload = make_payload()
    payload["location"] = []

    with pytest.raises(
        ValueError,
        match="location must be an object",
    ):
        json_schema.validate_payload(payload)


def test_rejects_missing_location_field() -> None:
    payload = make_payload()
    del payload["location"]["timezone"]

    with pytest.raises(
        ValueError,
        match="location is missing required fields",
    ):
        json_schema.validate_payload(payload)


def test_rejects_non_object_current() -> None:
    payload = make_payload()
    payload["current"] = []

    with pytest.raises(
        ValueError,
        match="current must be an object",
    ):
        json_schema.validate_payload(payload)


def test_rejects_missing_current_field() -> None:
    payload = make_payload()
    del payload["current"]["temperature"]

    with pytest.raises(
        ValueError,
        match="current is missing required fields",
    ):
        json_schema.validate_payload(payload)


def test_forecast_may_be_absent() -> None:
    payload = make_payload()

    json_schema.validate_payload(payload)

    assert "forecast" not in payload


def test_rejects_non_array_forecast() -> None:
    payload = make_payload()
    payload["forecast"] = {}

    with pytest.raises(
        ValueError,
        match="forecast must be an array",
    ):
        json_schema.validate_payload(payload)


def test_rejects_non_object_forecast_item() -> None:
    payload = make_payload()
    payload["forecast"] = ["bad"]

    with pytest.raises(
        ValueError,
        match=r"forecast\[0\] must be an object",
    ):
        json_schema.validate_payload(payload)


def test_rejects_missing_forecast_field() -> None:
    payload = make_payload()
    payload["forecast"] = [
        {
            "date": "2026-08-19",
        }
    ]

    with pytest.raises(
        ValueError,
        match=r"forecast\[0\] is missing required fields",
    ):
        json_schema.validate_payload(payload)
