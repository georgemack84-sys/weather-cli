import argparse
import logging
import sys

import requests
from rich.console import Console
from rich.table import Table

from weather_cli import __version__
from weather_cli.api import get_weather, search_locations
from weather_cli.cache import clear_cache
from weather_cli.config import (
    load_config,
    set_default_city,
    set_forecast_days,
    set_metric,
)
from weather_cli.logging_config import configure_logging
from weather_cli.normalization import normalize_weather_report
from weather_cli.renderers import json_renderer, rich_renderer

console = Console()
logger = logging.getLogger(__name__)


def build_weather_parser():
    """Build the parser used for normal weather requests."""

    parser = argparse.ArgumentParser(
        prog="weather",
        description=("A command-line weather application powered by Open-Meteo."),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "city",
        nargs="*",
        help="City to retrieve weather for",
    )

    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Display the daily forecast",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of forecast days (1-7)",
    )

    units = parser.add_mutually_exclusive_group()

    units.add_argument(
        "--metric",
        action="store_true",
        help="Use metric units",
    )

    units.add_argument(
        "--imperial",
        action="store_true",
        help="Use imperial units",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )

    return parser


def build_config_parser():
    """Build the parser used for configuration commands."""

    parser = argparse.ArgumentParser(
        prog="weather config",
        description="Manage Weather CLI configuration.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"weather {__version__}",
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
        help="Default city name",
    )

    set_days_parser = subparsers.add_parser(
        "set-days",
        help="Set the default number of forecast days",
    )

    set_days_parser.add_argument(
        "forecast_days",
        type=int,
        help="Forecast days (1-7)",
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
        help="Default unit system",
    )

    subparsers.add_parser(
        "show",
        help="Show the current configuration",
    )

    subparsers.add_parser(
        "clear-cache",
        help="Clear cached weather data",
    )

    return parser


def parse_arguments():
    """
    Parse Weather CLI arguments.

    The CLI intentionally uses separate weather and configuration
    parsers so arbitrary city names do not conflict with argparse
    subcommands.
    """

    raw_args = sys.argv[1:]

    if raw_args and raw_args[0] == "config":
        parser = build_config_parser()

        args = parser.parse_args(raw_args[1:])

        args.command = "config"

        return args

    parser = build_weather_parser()

    args = parser.parse_args(raw_args)

    args.command = "weather"

    return args


def resolve_preferences(args):
    """
    Resolve city, units, and forecast days.

    Command-line arguments take precedence over saved
    configuration values.
    """

    config = load_config()

    if args.city:
        city = " ".join(args.city)
    else:
        city = config.get("default_city")

    if args.metric:
        metric = True
    elif args.imperial:
        metric = False
    else:
        metric = config.get(
            "metric",
            False,
        )

    if args.days is not None:
        days = args.days
    else:
        days = config.get(
            "forecast_days",
            3,
        )

    return (
        city,
        metric,
        days,
    )


def choose_location(locations):
    """Allow the user to choose from multiple location matches."""

    if not locations:
        return None

    if len(locations) == 1:
        return locations[0]

    table = Table(title="Multiple locations found")

    table.add_column(
        "#",
        justify="right",
    )

    table.add_column("City")

    table.add_column("State")

    table.add_column("Country")

    for index, location in enumerate(
        locations,
        start=1,
    ):
        table.add_row(
            str(index),
            location.get(
                "name",
                "",
            ),
            location.get(
                "state",
                "",
            ),
            location.get(
                "country",
                "",
            ),
        )

    console.print(table)

    while True:
        selection = console.input(
            "[bold]Choose a location (number or q to cancel): [/bold]"
        )

        selection = selection.strip()

        if selection.lower() == "q":
            return None

        try:
            index = int(selection)
        except ValueError:
            console.print("[red]Please enter a valid number or q to cancel.[/red]")

            continue

        if not 1 <= index <= len(locations):
            console.print("[red]That location number is out of range.[/red]")

            continue

        return locations[index - 1]


def display_configuration():
    """Display the current Weather CLI configuration."""

    config = load_config()

    table = Table(title="Weather CLI Configuration")

    table.add_column("Setting")

    table.add_column("Value")

    default_city = config.get("default_city") or "Not configured"

    units = (
        "metric"
        if config.get(
            "metric",
            False,
        )
        else "imperial"
    )

    forecast_days = config.get(
        "forecast_days",
        3,
    )

    table.add_row(
        "Default city",
        str(default_city),
    )

    table.add_row(
        "Units",
        units,
    )

    table.add_row(
        "Forecast days",
        str(forecast_days),
    )

    console.print(table)


def handle_config(args):
    """Handle Weather CLI configuration commands."""

    if args.config_command == "set-city":
        city = " ".join(args.default_city)

        set_default_city(city)

        console.print(f"[green]Default city set to {city}.[/green]")

        return

    if args.config_command == "set-days":
        try:
            set_forecast_days(args.forecast_days)
        except ValueError as error:
            console.print(f"[red]{error}[/red]")

            return

        console.print(
            f"[green]Default forecast days set to {args.forecast_days}.[/green]"
        )

        return

    if args.config_command == "set-units":
        metric = args.units == "metric"

        set_metric(metric)

        console.print(f"[green]Default units set to {args.units}.[/green]")

        return

    if args.config_command == "show":
        display_configuration()
        return

    if args.config_command == "clear-cache":
        clear_cache()

        console.print("[green]Weather cache cleared.[/green]")

        return

    console.print(
        "Use [bold]weather config --help[/bold] "
        "to see available configuration commands."
    )


def run_weather(args):
    """Run a weather lookup."""

    try:
        (
            city,
            metric,
            days,
        ) = resolve_preferences(args)

        json_output = getattr(args, "json", False)

        if not city:
            console.print(
                "[red]No city specified.[/red]\n"
                "\n"
                "Provide a city on the command line:\n"
                "  weather Atlanta\n"
                "\n"
                "Or configure a default city:\n"
                "  weather config set-city Atlanta"
            )

            return

        if not 1 <= days <= 7:
            console.print("[red]Forecast days must be between 1 and 7.[/red]")

            return

        logger.info(
            "Searching for location: %s",
            city,
        )

        locations = search_locations(city)

        if not locations:
            console.print(f"[red]Could not find '{city}'.[/red]")

            return

        if json_output:
            location = locations[0]
        else:
            location = choose_location(locations)

            if location is None:
                console.print("[yellow]Search cancelled.[/yellow]")

                return

        latitude = location["latitude"]

        longitude = location["longitude"]

        logger.info(
            "Retrieving weather for %s",
            location.get(
                "name",
                city,
            ),
        )

        weather = get_weather(
            latitude,
            longitude,
            days,
            metric,
        )

        report = normalize_weather_report(
            location=location,
            weather=weather,
            metric=metric,
            include_forecast=args.forecast,
        )

        if json_output:
            if args.forecast:
                json_renderer.render_forecast(report)
            else:
                json_renderer.render_current(report)

        else:
            rich_renderer.render_current(report)

            if args.forecast:
                rich_renderer.render_forecast(
                    weather,
                    metric,
                )

    except requests.exceptions.Timeout:
        logger.exception("Weather request timed out")

        console.print("[red]The weather request timed out. Please try again.[/red]")

    except requests.exceptions.ConnectionError:
        logger.exception("Unable to connect to weather service")

        console.print(
            "[red]Unable to connect to the weather "
            "service. Check your internet connection."
            "[/red]"
        )

    except requests.exceptions.HTTPError as error:
        logger.exception("Weather service returned an HTTP error")

        console.print(
            f"[red]HTTP error while contacting the weather service: {error}[/red]"
        )

    except requests.exceptions.RequestException as error:
        logger.exception("Weather request failed")

        console.print(
            f"[red]Request error while contacting the weather service: {error}[/red]"
        )

    except KeyError as error:
        logger.exception("Unexpected weather data")

        console.print(
            f"[red]The weather service returned unexpected data: {error}[/red]"
        )

    except ValueError as error:
        logger.exception("Invalid weather data")

        console.print(f"[red]Data error: {error}[/red]")

    except Exception as error:
        logger.exception("Unexpected Weather CLI error")

        console.print(f"[red]Unexpected error: {error}[/red]")


def main():
    """Weather CLI entry point."""

    configure_logging()

    args = parse_arguments()

    if args.command == "config":
        handle_config(args)
        return

    run_weather(args)


if __name__ == "__main__":
    main()
