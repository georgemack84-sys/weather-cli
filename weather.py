import argparse

import requests

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Heavy Drizzle",
    56: "Light Freezing Drizzle",
    57: "Heavy Freezing Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Rain Showers",
    81: "Moderate Rain Showers",
    82: "Heavy Rain Showers",
    85: "Light Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail",
    99: "Severe Thunderstorm with Hail",
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Get current weather and forecasts from the terminal."
    )

    parser.add_argument(
        "city",
        nargs="+",
        help="City to look up, such as Atlanta or New York",
    )

    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Show the daily forecast",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Number of forecast days to display (1-7)",
    )

    parser.add_argument(
        "--metric",
        action="store_true",
        help="Use Celsius and km/h instead of Fahrenheit and mph",
    )

    return parser.parse_args()


def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    location = data["results"][0]

    return {
        "name": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "country": location.get("country", ""),
        "state": location.get("admin1", ""),
    }


def get_weather(latitude, longitude, days, metric):
    url = "https://api.open-meteo.com/v1/forecast"

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
        ],
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
        "forecast_days": days,
        "timezone": "auto",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_wind_direction(degrees):
    directions = [
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW",
    ]

    index = round(degrees / 45) % 8
    return directions[index]


def format_location(location):
    parts = [location["name"]]

    if location["state"]:
        parts.append(location["state"])

    return ", ".join(parts)


def display_current_weather(location, weather, metric):
    current = weather["current"]

    condition = WEATHER_CODES.get(
        current["weather_code"],
        "Unknown",
    )

    wind_direction = get_wind_direction(current["wind_direction_10m"])

    location_name = format_location(location)

    temperature_symbol = "°C" if metric else "°F"
    wind_unit = "km/h" if metric else "mph"
    precipitation_unit = "mm" if metric else "in"

    print()
    print("=" * 54)
    print("                    WEATHER CLI")
    print("=" * 54)

    print(f"Location:      {location_name}")
    print(f"Country:       {location['country']}")

    print("-" * 54)

    print(f"Conditions:    {condition}")
    print(f"Temperature:   {current['temperature_2m']} {temperature_symbol}")
    print(f"Feels Like:    {current['apparent_temperature']} {temperature_symbol}")
    print(f"Humidity:      {current['relative_humidity_2m']}%")
    print(f"Precipitation: {current['precipitation']} {precipitation_unit}")

    print("-" * 54)

    print(f"Wind:          {current['wind_speed_10m']} {wind_unit} {wind_direction}")
    print(f"Wind Gusts:    {current['wind_gusts_10m']} {wind_unit}")

    print("=" * 54)


def display_forecast(weather, metric):
    daily = weather["daily"]

    temperature_symbol = "°C" if metric else "°F"

    print()
    print("FORECAST")
    print("=" * 72)

    for index in range(len(daily["time"])):
        date = daily["time"][index]

        condition = WEATHER_CODES.get(
            daily["weather_code"][index],
            "Unknown",
        )

        high = daily["temperature_2m_max"][index]
        low = daily["temperature_2m_min"][index]
        rain = daily["precipitation_probability_max"][index]

        print(
            f"{date} | "
            f"{condition:<25} | "
            f"High {high:>5} {temperature_symbol} | "
            f"Low {low:>5} {temperature_symbol} | "
            f"Rain {rain}%"
        )

    print("=" * 72)


def main():
    args = parse_arguments()

    city = " ".join(args.city)

    if args.days < 1 or args.days > 7:
        print("Error: --days must be between 1 and 7.")
        return

    print()
    print(f"Searching for {city}...")

    try:
        location = get_coordinates(city)

        if location is None:
            print()
            print(f"Could not find '{city}'.")
            print("Check the spelling and try again.")
            return

        weather = get_weather(
            location["latitude"],
            location["longitude"],
            args.days,
            args.metric,
        )

        display_current_weather(
            location,
            weather,
            args.metric,
        )

        if args.forecast:
            display_forecast(
                weather,
                args.metric,
            )

    except requests.exceptions.Timeout:
        print()
        print("Error: The weather service took too long to respond.")

    except requests.exceptions.ConnectionError:
        print()
        print("Error: Unable to connect to the weather service.")
        print("Check your internet connection.")

    except requests.exceptions.HTTPError as error:
        print()
        print("Error: The weather service returned an HTTP error.")
        print(error)

    except requests.exceptions.RequestException as error:
        print()
        print("Error: Unable to retrieve weather information.")
        print(error)

    except KeyError as error:
        print()
        print("Error: Unexpected weather data received.")
        print(f"Missing field: {error}")


if __name__ == "__main__":
    main()
