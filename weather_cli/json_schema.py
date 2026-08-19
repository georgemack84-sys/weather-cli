"""Versioned JSON contract definitions for Weather CLI."""

from __future__ import annotations

SCHEMA_VERSION = "1"

VALID_UNIT_SYSTEMS = {
    "metric",
    "imperial",
}


def validate_payload(payload: dict) -> None:
    """Validate a Weather CLI JSON payload against schema version 1."""

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema version: {payload.get('schema_version')!r}"
        )

    units = payload.get("units")

    if units not in VALID_UNIT_SYSTEMS:
        raise ValueError(f"Invalid units value: {units!r}")

    location = payload.get("location")

    if not isinstance(location, dict):
        raise ValueError("location must be an object")

    required_location_fields = {
        "name",
        "state",
        "country",
        "latitude",
        "longitude",
        "timezone",
    }

    missing_location = required_location_fields - location.keys()

    if missing_location:
        raise ValueError(
            "location is missing required fields: "
            + ", ".join(sorted(missing_location))
        )

    current = payload.get("current")

    if not isinstance(current, dict):
        raise ValueError("current must be an object")

    required_current_fields = {
        "temperature",
        "feels_like",
        "humidity",
        "weather",
        "weather_code",
        "wind_speed",
        "wind_direction",
        "wind_gusts",
        "precipitation",
    }

    missing_current = required_current_fields - current.keys()

    if missing_current:
        raise ValueError(
            "current is missing required fields: " + ", ".join(sorted(missing_current))
        )

    forecast = payload.get("forecast")

    if forecast is None:
        return

    if not isinstance(forecast, list):
        raise ValueError("forecast must be an array")

    required_forecast_fields = {
        "date",
        "weather",
        "temperature_max",
        "temperature_min",
        "precipitation_probability",
        "precipitation",
        "wind_speed_max",
    }

    for index, item in enumerate(forecast):
        if not isinstance(item, dict):
            raise ValueError(f"forecast[{index}] must be an object")

        missing_forecast = required_forecast_fields - item.keys()

        if missing_forecast:
            raise ValueError(
                f"forecast[{index}] is missing required fields: "
                + ", ".join(sorted(missing_forecast))
            )
