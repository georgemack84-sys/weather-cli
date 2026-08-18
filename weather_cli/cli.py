import argparse
import logging
import sys

import requests
from rich.console import Console
from rich.table import Table

from weather_cli.api import get_weather, search_locations
from weather_cli.cache import clear_cache
from weather_cli.config import (
    load_config,
    set_default_city,
    set_forecast_days,
    set_metric,
)
from weather_cli.display import (
    display_current_weather,
    display_forecast,
)
from weather_cli.logging_config import configure_logging


console = Console()
logger = logging.getLogger(__name__)


def build_weather_parser():
    """
    Build the parser used for normal weather lookups.
    """

    parser = argparse.ArgumentParser(
        prog="weather",
        description=(
            "Get current weather and forecasts "
            "from the terminal."
        ),
    )

    parser.add_argument(
        "city",
        nargs="*",
        help="City or location to look up",
    )

    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Show the daily forecast",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of forecast days (1-7)",
    )

    unit_group = parser.add_mutually_exclusive_group()

    unit_group.add_argument(
        "--metric",
        action="store_true",
        help="Use metric units",
    )

    unit_group.add_argument(
        "--imperial",
        action="store_true",
        help="Use imperial units",
    )

    return parser


def build_config_parser():
    """
    Build the parser used for Weather CLI
    configuration commands.
    """

    parser = argparse.ArgumentParser(
        prog="weather config",
        description="Manage Weather CLI configuration.",
    )

    subparsers = parser.add_subparsers(
        dest="config_command",
    )

    set_city_parser = subparsers.add_parser(
        "set-city",
        help="Set the default city",
    )

    set_city_parser.add_argument(
        "default_city",
        nargs="+",
        help="City to use by default",
    )

    set_days_parser = subparsers.add_parser(
        "set-days",
        help="Set the default forecast length",
    )

    set_days_parser.add_argument(
        "forecast_days",
        type=int,
        help="Number of forecast days (1-7)",
    )

    set_units_parser = subparsers.add_parser(
        "set-units",
        help="Set the default unit system",
    )

    set_units_parser.add_argument(
        "units",
        choices=[
            "metric",
            "imperial",
        ],
        help="Preferred measurement system",
    )

    subparsers.add_parser(
        "show",
        help="Show current configuration",
    )

    subparsers.add_parser(
        "clear-cache",
        help="Clear cached weather data",
    )

    return parser


def parse_arguments():
    """
    Determine whether the user requested a normal
    weather lookup or a configuration command.
    """

    arguments = sys.argv[1:]

    if arguments and arguments[0] == "config":
        parser = build_config_parser()

        args = parser.parse_args(
            arguments[1:]
        )

        args.command = "config"

        return args

    parser = build_weather_parser()

    args = parser.parse_args(
        arguments
    )

    args.command = "weather"

    return args


def display_location_choices(locations):
    """
    Display multiple matching locations in
    a Rich table.
    """

    table = Table(
        title="Multiple Locations Found",
        show_header=True,
        header_style="bold",
    )

    table.add_column(
        "#",
        justify="right",
    )

    table.add_column("City")
    table.add_column("State / Region")
    table.add_column("Country")
    table.add_column("Timezone")

    for index, location in enumerate(
        locations,
        start=1,
    ):
        table.add_row(
            str(index),
            location["name"],
            location["state"] or "-",
            location["country"] or "-",
            location["timezone"] or "-",
        )

    console.print()
    console.print(table)


def choose_location(locations):
    """
    Allow the user to choose between multiple
    geocoding results.
    """

    if len(locations) == 1:
        return locations[0]

    display_location_choices(
        locations
    )

    while True:
        choice = console.input(
            "\nSelect location "
            f"[1-{len(locations)}], "
            "or Q to quit: "
        ).strip()

        if choice.lower() == "q":
            logger.info(
                "User cancelled location selection"
            )

            return None

        try:
            index = int(choice)

            if 1 <= index <= len(locations):
                selected = locations[
                    index - 1
                ]

                logger.info(
                    (
                        "Location selected: "
                        "name=%s state=%s country=%s"
                    ),
                    selected["name"],
                    selected["state"],
                    selected["country"],
                )

                return selected

        except ValueError:
            pass

        console.print(
            "[yellow]"
            "Please enter a valid number "
            "or Q to quit."
            "[/yellow]"
        )


def display_configuration():
    """
    Display the current saved configuration.
    """

    config = load_config()

    units = (
        "metric"
        if config["metric"]
        else "imperial"
    )

    console.print()
    console.print(
        "[bold]Weather CLI Configuration[/bold]"
    )

    console.print(
        "Default city:     "
        f"{config['default_city'] or 'Not set'}"
    )

    console.print(
        f"Default units:    {units}"
    )

    console.print(
        "Forecast days:    "
        f"{config['forecast_days']}"
    )


def handle_config(args):
    """
    Process configuration commands.
    """

    if args.config_command == "set-city":
        city = " ".join(
            args.default_city
        )

        set_default_city(
            city
        )

        logger.info(
            "Default city updated: %s",
            city,
        )

        console.print(
            f"[green]"
            f"Default city set to {city}."
            f"[/green]"
        )

        return

    if args.config_command == "set-days":
        try:
            set_forecast_days(
                args.forecast_days
            )

        except ValueError as error:
            logger.warning(
                (
                    "Invalid default forecast "
                    "days requested: %s"
                ),
                args.forecast_days,
            )

            console.print(
                f"[red]Error:[/red] {error}"
            )

            return

        logger.info(
            "Default forecast days updated: %s",
            args.forecast_days,
        )

        console.print(
            "[green]"
            "Default forecast days set to "
            f"{args.forecast_days}."
            "[/green]"
        )

        return

    if args.config_command == "set-units":
        metric = (
            args.units == "metric"
        )

        set_metric(
            metric
        )

        logger.info(
            "Default units updated: %s",
            args.units,
        )

        console.print(
            "[green]"
            f"Default units set to "
            f"{args.units}."
            "[/green]"
        )

        return

    if args.config_command == "show":
        logger.info(
            "Displaying configuration"
        )

        display_configuration()

        return

    if args.config_command == "clear-cache":
        clear_cache()

        logger.info(
            "Weather cache cleared"
        )

        console.print(
            "[green]"
            "Weather cache cleared."
            "[/green]"
        )

        return

    console.print(
        "Use 'weather config --help' "
        "to see configuration commands."
    )


def resolve_preferences(args):
    """
    Combine command-line arguments with saved
    configuration values.

    Command-line values take precedence over
    saved defaults.
    """

    config = load_config()

    if args.city:
        city = " ".join(
            args.city
        )
    else:
        city = config["default_city"]

    if args.metric:
        metric = True

    elif args.imperial:
        metric = False

    else:
        metric = config["metric"]

    if args.days is not None:
        days = args.days

    else:
        days = config["forecast_days"]

    return (
        city,
        metric,
        days,
    )


def run_weather(args):
    """
    Perform the weather lookup.
    """

    city, metric, days = resolve_preferences(
        args
    )

    if city is None:
        logger.info(
            "Weather command used without a city"
        )

        console.print()
        console.print(
            "[yellow]"
            "No city specified."
            "[/yellow]"
        )

        console.print()
        console.print(
            "Try:"
        )

        console.print(
            "  weather Atlanta"
        )

        console.print()
        console.print(
            "Or set a default city:"
        )

        console.print(
            "  weather config set-city Atlanta"
        )

        return

    if not 1 <= days <= 7:
        logger.warning(
            "Invalid forecast day count: %s",
            days,
        )

        console.print(
            "[red]Error:[/red] "
            "--days must be between 1 and 7."
        )

        return

    logger.info(
        (
            "Weather lookup started: "
            "city=%s days=%s metric=%s "
            "forecast=%s"
        ),
        city,
        days,
        metric,
        args.forecast,
    )

    console.print()
    console.print(
        f"Searching for "
        f"[bold]{city}[/bold]..."
    )

    try:
        locations = search_locations(
            city
        )

        if not locations:
            logger.info(
                "No locations found: %s",
                city,
            )

            console.print()
            console.print(
                f"[red]"
                f"Could not find '{city}'."
                f"[/red]"
            )

            console.print(
                "Try including a state, "
                "province, or country."
            )

            return

        logger.info(
            "Location search returned %s matches",
            len(locations),
        )

        location = choose_location(
            locations
        )

        if location is None:
            console.print(
                "Search cancelled."
            )

            return

        weather = get_weather(
            location["latitude"],
            location["longitude"],
            days,
            metric,
        )

        display_current_weather(
            location,
            weather,
            metric,
        )

        if args.forecast:
            display_forecast(
                weather,
                metric,
            )

        logger.info(
            (
                "Weather lookup completed: "
                "city=%s state=%s country=%s"
            ),
            location["name"],
            location["state"],
            location["country"],
        )

    except requests.exceptions.Timeout:
        logger.exception(
            "Weather request timed out"
        )

        console.print()
        console.print(
            "[red]Error:[/red] "
            "Weather service request timed out."
        )

    except requests.exceptions.ConnectionError:
        logger.exception(
            "Weather service connection failed"
        )

        console.print()
        console.print(
            "[red]Error:[/red] "
            "Unable to connect to the "
            "weather service."
        )

        console.print(
            "Check your internet connection."
        )

    except requests.exceptions.HTTPError as error:
        logger.exception(
            "Weather service HTTP error"
        )

        console.print()
        console.print(
            "[red]HTTP error:[/red] "
            f"{error}"
        )

    except requests.exceptions.RequestException as error:
        logger.exception(
            "Weather service request failed"
        )

        console.print()
        console.print(
            "[red]Request error:[/red] "
            f"{error}"
        )

    except KeyError as error:
        logger.exception(
            "Required weather data field missing"
        )

        console.print()
        console.print(
            "[red]Data error:[/red] "
            "The weather service returned "
            "unexpected data."
        )

        console.print(
            f"Missing field: {error}"
        )

    except ValueError as error:
        logger.exception(
            "Weather data processing failed"
        )

        console.print()
        console.print(
            "[red]Data error:[/red] "
            f"{error}"
        )

    except Exception:
        logger.exception(
            "Unexpected Weather CLI error"
        )

        console.print()
        console.print(
            "[red]Unexpected error:[/red] "
            "Weather CLI encountered a problem."
        )

        console.print(
            "Check the application log "
            "for additional details."
        )


def main():
    """
    Main Weather CLI entry point.
    """

    configure_logging()

    logger.info(
        "Weather CLI started"
    )

    args = parse_arguments()

    try:
        if args.command == "config":
            handle_config(
                args
            )

            return

        run_weather(
            args
        )

    finally:
        logger.info(
            "Weather CLI finished"
        )


if __name__ == "__main__":
    main()