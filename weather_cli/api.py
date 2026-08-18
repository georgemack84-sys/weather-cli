import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city):
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("results"):
        return None

    result = data["results"][0]

    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country", ""),
        "state": result.get("admin1", ""),
        "timezone": result.get("timezone", ""),
    }


def get_weather(latitude, longitude, days, metric):
    if metric:
        temperature_unit = "celsius"
        wind_speed_unit = "kmh"
        precipitation_unit = "mm"
    else:
        temperature_unit = "fahrenheit"
        wind_speed_unit = "mph"
        precipitation_unit = "inch"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
        ],

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum",
            "wind_speed_10m_max",
            "sunrise",
            "sunset",
        ],

        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
        "forecast_days": days,
        "timezone": "auto",
    }

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()