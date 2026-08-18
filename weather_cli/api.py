import requests

from weather_cli.cache import load_cache, save_cache


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def search_locations(city, count=5):
    """
    Search for matching locations using the Open-Meteo
    geocoding service.

    Returns a list of location dictionaries.
    """

    params = {
        "name": city,
        "count": count,
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
    results = data.get("results", [])

    locations = []

    for result in results:
        locations.append(
            {
                "name": result["name"],
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "country": result.get("country", ""),
                "country_code": result.get("country_code", ""),
                "state": result.get("admin1", ""),
                "county": result.get("admin2", ""),
                "timezone": result.get("timezone", ""),
                "population": result.get("population"),
            }
        )

    return locations


def build_weather_cache_key(
    latitude,
    longitude,
    days,
    metric,
):
    """
    Build a unique cache key for a weather request.

    The key includes coordinates, forecast length,
    and unit system so different requests do not
    overwrite one another.
    """

    unit_system = (
        "metric"
        if metric
        else "imperial"
    )

    return (
        f"weather_"
        f"{latitude}_"
        f"{longitude}_"
        f"{days}_"
        f"{unit_system}"
    )


def get_weather(
    latitude,
    longitude,
    days,
    metric,
):
    """
    Retrieve weather data from Open-Meteo.

    A recent cached response is returned when available.
    Otherwise, the API is called and the result is cached.
    """

    cache_key = build_weather_cache_key(
        latitude,
        longitude,
        days,
        metric,
    )

    cached_weather = load_cache(
        cache_key
    )

    if cached_weather is not None:
        return cached_weather

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

    weather = response.json()

    save_cache(
        cache_key,
        weather,
    )

    return weather