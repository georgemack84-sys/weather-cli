from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from weather_cli.weather_codes import get_weather_description

console = Console()


def get_wind_direction(degrees):
    """Convert wind direction in degrees to a compass direction."""

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
    """Create a readable location name."""

    parts = [location["name"]]

    if location["state"]:
        parts.append(location["state"])

    return ", ".join(parts)


def get_units(metric):
    """Return display units."""

    if metric:
        return {
            "temperature": "°C",
            "wind": "km/h",
            "precipitation": "mm",
        }

    return {
        "temperature": "°F",
        "wind": "mph",
        "precipitation": "in",
    }


def get_weather_icon(code):
    """Return a simple weather symbol for a WMO weather code."""

    if code == 0:
        return "☀"

    if code in (1, 2):
        return "⛅"

    if code == 3:
        return "☁"

    if code in (45, 48):
        return "🌫"

    if code in (51, 53, 55, 56, 57):
        return "🌦"

    if code in (61, 63, 65, 66, 67):
        return "🌧"

    if code in (71, 73, 75, 77, 85, 86):
        return "❄"

    if code in (80, 81, 82):
        return "🌦"

    if code in (95, 96, 99):
        return "⛈"

    return "?"


def display_current_weather(location, weather, metric):
    """Display current weather using a Rich panel."""

    current = weather["current"]
    units = get_units(metric)

    weather_code = current["weather_code"]

    condition = get_weather_description(weather_code)
    icon = get_weather_icon(weather_code)

    wind_direction = get_wind_direction(current["wind_direction_10m"])

    location_name = format_location(location)

    content = Text()

    content.append(
        f"{icon}  {condition}\n\n",
        style="bold",
    )

    content.append("Temperature     ")
    content.append(
        f"{current['temperature_2m']} {units['temperature']}\n",
        style="bold",
    )

    content.append("Feels Like      ")
    content.append(f"{current['apparent_temperature']} {units['temperature']}\n")

    content.append("Humidity        ")
    content.append(f"{current['relative_humidity_2m']}%\n")

    content.append("Precipitation   ")
    content.append(f"{current['precipitation']} {units['precipitation']}\n")

    content.append("Wind            ")
    content.append(f"{current['wind_speed_10m']} {units['wind']} {wind_direction}\n")

    content.append("Wind Gusts      ")
    content.append(f"{current['wind_gusts_10m']} {units['wind']}")

    subtitle_parts = [location["country"]]

    if location["timezone"]:
        subtitle_parts.append(location["timezone"])

    console.print()

    console.print(
        Panel(
            content,
            title=f"[bold]{location_name}[/bold]",
            subtitle=" • ".join(subtitle_parts),
            expand=False,
            padding=(1, 3),
        )
    )


def display_forecast(weather, metric):
    """Display daily forecast using a Rich table."""

    daily = weather["daily"]
    units = get_units(metric)

    table = Table(
        title="Daily Forecast",
        show_header=True,
        header_style="bold",
    )

    table.add_column("Date")
    table.add_column("Weather")
    table.add_column("High", justify="right")
    table.add_column("Low", justify="right")
    table.add_column("Rain", justify="right")
    table.add_column("Wind", justify="right")
    table.add_column("Sunrise")
    table.add_column("Sunset")

    for index, date in enumerate(daily["time"]):
        code = daily["weather_code"][index]

        condition = get_weather_description(code)
        icon = get_weather_icon(code)

        high = daily["temperature_2m_max"][index]
        low = daily["temperature_2m_min"][index]

        rain_probability = daily["precipitation_probability_max"][index]

        max_wind = daily["wind_speed_10m_max"][index]

        sunrise = daily["sunrise"][index]
        sunset = daily["sunset"][index]

        if "T" in sunrise:
            sunrise = sunrise.split("T")[1]

        if "T" in sunset:
            sunset = sunset.split("T")[1]

        table.add_row(
            date,
            f"{icon} {condition}",
            f"{high} {units['temperature']}",
            f"{low} {units['temperature']}",
            f"{rain_probability}%",
            f"{max_wind} {units['wind']}",
            sunrise,
            sunset,
        )

    console.print()
    console.print(table)
