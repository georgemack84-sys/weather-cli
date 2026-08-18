import argparse

import requests
from rich.console import Console
from rich.table import Table

from weather_cli.api import get_weather, search_locations
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


console = Console()


def build_weather_parser():
    """Build the parser used for normal weather lookups."""

    parser = argparse.ArgumentParser(
        prog="weather",
        description="Get current weather and forecasts from the terminal.",
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
    """Build the parser used for configuration commands."""

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
    )

    subparsers.add_parser(
        "show",
        help="Show current configuration",
    )

    return parser


def parse_arguments():
    """
    Determine whether the user wants a normal weather lookup
    or a configuration command.
    """

    import sys

    arguments = sys.argv[1:]

    if arguments and arguments[0] == "config":
        parser = build_config_parser()

        args = parser.parse_args(
            arguments[1:]
        )

        args.command = "config"

        return args

    parser = build_weather_parser()

    args = parser.parse_args(arguments)

    args.command = "weather"

    return args


def display_location_choices(locations):
    """Display multiple matching locations."""

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
    """Allow the user to select from multiple locations."""

    if len(locations) == 1:
        return locations[0]

    display_location_choices(locations)

    while True:
        choice = console.input(
            "\nSelect location "
            f"[1-{len(locations)}], "
            "or Q to quit: "
        ).strip()

        if choice.lower() == "q":
            return None

        try:
            index = int(choice)

            if 1 <= index <= len(locations):
                return locations[index - 1]

        except ValueError:
            pass

        console.print(
            "[yellow]"
            "Please enter a valid number or Q to quit."
            "[/yellow]"
        )


def handle_config(args):
    """Process configuration commands."""

    if args.config_command == "set-city":
        city = " ".join(
            args.default_city
        )

        set_default_city(city)

        console.print(
            f"[green]Default city set to {city}.[/green]"
        )

        return

    if args.config_command == "set-days":
        try:
            set_forecast_days(
                args.forecast_days
            )

        except ValueError as error:
            console.print(
                f"[red]Error:[/red] {error}"
            )

            return

        console.print(
            "[green]"
            f"Default forecast days set to "
            f"{args.forecast_days}."
            "[/green]"
        )

        return

    if args.config_command == "set-units":
        metric = (
            args.units == "metric"
        )

        set_metric(metric)

        console.print(
            "[green]"
            f"Default units set to {args.units}."
            "[/green]"
        )

        return

    if args.config_command == "show":
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

        return

    console.print(
        "Use 'weather config --help' "
        "to see configuration commands."
    )


def resolve_preferences(args):
    """Combine CLI arguments with saved configuration."""

    config = load_config()

    if args.city:
        city = " ".join(args.city)
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

    return city, metric, days


def run_weather(args):
    """Run a weather lookup."""

    city, metric, days = resolve_preferences(args)

    if city is None:
        console.print()
        console.print(
            "[yellow]No city specified.[/yellow]"
        )

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
        console.print(
            "[red]Error:[/red] "
            "--days must be between 1 and 7."
        )

        return

    console.print()
    console.print(
        f"Searching for [bold]{city}[/bold]..."
    )

    try:
        locations = search_locations(city)

        if not locations:
            console.print()
            console.print(
                f"[red]Could not find '{city}'.[/red]"
            )

            console.print(
                "Try including a state, province, "
                "or country."
            )

            return

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

    except requests.exceptions.Timeout:
        console.print()
        console.print(
            "[red]Error:[/red] "
            "Weather service request timed out."
        )

    except requests.exceptions.ConnectionError:
        console.print()
        console.print(
            "[red]Error:[/red] "
            "Unable to connect to the weather service."
        )

    except requests.exceptions.HTTPError as error:
        console.print()
        console.print(
            f"[red]HTTP error:[/red] {error}"
        )

    except requests.exceptions.RequestException as error:
        console.print()
        console.print(
            f"[red]Request error:[/red] {error}"
        )

    except (KeyError, ValueError) as error:
        console.print()
        console.print(
            f"[red]Data error:[/red] {error}"
        )


def main():
    """Main Weather CLI entry point."""

    args = parse_arguments()

    if args.command == "config":
        handle_config(args)
        return

    run_weather(args)


if __name__ == "__main__":
    main()