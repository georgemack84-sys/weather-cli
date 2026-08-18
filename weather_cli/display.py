from weather_cli.weather_codes import get_weather_description


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


def get_units(metric):
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


def display_current_weather(location, weather, metric):
    current = weather["current"]
    units = get_units(metric)

    condition = get_weather_description(
        current["weather_code"]
    )

    wind_direction = get_wind_direction(
        current["wind_direction_10m"]
    )

    print()
    print("=" * 58)
    print("                      WEATHER CLI")
    print("=" * 58)

    print(f"Location:        {format_location(location)}")
    print(f"Country:         {location['country']}")

    if location["timezone"]:
        print(f"Timezone:        {location['timezone']}")

    print("-" * 58)

    print(f"Conditions:      {condition}")

    print(
        f"Temperature:     "
        f"{current['temperature_2m']} "
        f"{units['temperature']}"
    )

    print(
        f"Feels Like:      "
        f"{current['apparent_temperature']} "
        f"{units['temperature']}"
    )

    print(
        f"Humidity:        "
        f"{current['relative_humidity_2m']}%"
    )

    print(
        f"Precipitation:   "
        f"{current['precipitation']} "
        f"{units['precipitation']}"
    )

    print("-" * 58)

    print(
        f"Wind:            "
        f"{current['wind_speed_10m']} "
        f"{units['wind']} "
        f"{wind_direction}"
    )

    print(
        f"Wind Gusts:      "
        f"{current['wind_gusts_10m']} "
        f"{units['wind']}"
    )

    print("=" * 58)


def display_forecast(weather, metric):
    daily = weather["daily"]
    units = get_units(metric)

    print()
    print("DAILY FORECAST")
    print("=" * 78)

    for index, date in enumerate(daily["time"]):
        condition = get_weather_description(
            daily["weather_code"][index]
        )

        high = daily["temperature_2m_max"][index]
        low = daily["temperature_2m_min"][index]

        rain_probability = daily[
            "precipitation_probability_max"
        ][index]

        precipitation = daily[
            "precipitation_sum"
        ][index]

        max_wind = daily[
            "wind_speed_10m_max"
        ][index]

        sunrise = daily["sunrise"][index]
        sunset = daily["sunset"][index]

        if "T" in sunrise:
            sunrise = sunrise.split("T")[1]

        if "T" in sunset:
            sunset = sunset.split("T")[1]

        print()
        print(date)
        print("-" * 78)

        print(f"Conditions:      {condition}")

        print(
            f"High / Low:      "
            f"{high} {units['temperature']} / "
            f"{low} {units['temperature']}"
        )

        print(f"Rain Chance:     {rain_probability}%")

        print(
            f"Precipitation:   "
            f"{precipitation} "
            f"{units['precipitation']}"
        )

        print(
            f"Max Wind:        "
            f"{max_wind} {units['wind']}"
        )

        print(f"Sunrise:         {sunrise}")
        print(f"Sunset:          {sunset}")

    print()
    print("=" * 78)