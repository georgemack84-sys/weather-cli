import argparse

import requests

from weather_cli.api import get_coordinates, get_weather
from weather_cli.display import (
    display_current_weather,
    display_forecast,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="weather",
        description=(
            "Get current weather and forecasts "
            "from the terminal."
        ),
    )

    parser.add_argument(
        "city",
        nargs="+",
        help="City to look up",
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
        help="Number of forecast days (1-7)",
    )

    parser.add_argument(
        "--metric",
        action="store_true",
        help="Use metric units",
    )

    return parser.parse_args()


def validate_arguments(args):
    if not 1 <= args.days <= 7:
        print("Error: --days must be between 1 and 7.")
        return False

    return True


def main():
    args = parse_arguments()

    if not validate_arguments(args):
        return

    city = " ".join(args.city)

    print()
    print(f"Searching for {city}...")

    try:
        location = get_coordinates(city)

        if location is None:
            print()
            print(f"Could not find '{city}'.")
            print("Check the city name and try again.")
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
        print("Error: Weather service request timed out.")

    except requests.exceptions.ConnectionError:
        print()
        print("Error: Unable to connect to the weather service.")
        print("Check your internet connection.")

    except requests.exceptions.HTTPError as error:
        print()
        print("Error: Weather service returned an HTTP error.")
        print(error)

    except requests.exceptions.RequestException as error:
        print()
        print("Error: Unable to retrieve weather information.")
        print(error)

    except (KeyError, ValueError) as error:
        print()
        print("Error: Unable to process weather data.")
        print(error)


if __name__ == "__main__":
    main()