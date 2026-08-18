import json
from pathlib import Path


APP_DIRECTORY = Path.home() / ".weather-cli"
CONFIG_FILE = APP_DIRECTORY / "config.json"


DEFAULT_CONFIG = {
    "default_city": None,
    "metric": False,
    "forecast_days": 3,
}


def load_config():
    """
    Load the Weather CLI configuration.

    If the configuration file does not exist, cannot be read,
    contains invalid JSON, or does not contain a dictionary,
    return a copy of DEFAULT_CONFIG.
    """

    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            saved_config = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return DEFAULT_CONFIG.copy()

    if not isinstance(saved_config, dict):
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG.copy()

    config.update(
        {
            key: value
            for key, value in saved_config.items()
            if key in DEFAULT_CONFIG
        }
    )

    return config


def save_config(config):
    """
    Save the Weather CLI configuration to disk.
    """

    APP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with CONFIG_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            config,
            file,
            indent=4,
        )


def set_default_city(city):
    """
    Set the default city.

    Passing None, an empty string, or whitespace-only text
    clears the saved default city.
    """

    config = load_config()

    if city is None:
        config["default_city"] = None

    else:
        city = city.strip()

        config["default_city"] = (
            city
            if city
            else None
        )

    save_config(
        config
    )


def set_metric(metric):
    """
    Set the default measurement system.

    True means metric.
    False means imperial.
    """

    config = load_config()

    config["metric"] = bool(metric)

    save_config(
        config
    )


def set_forecast_days(days):
    """
    Set the default forecast length.

    Valid values are integers from 1 through 7.
    """

    if not isinstance(days, int):
        raise TypeError(
            "Forecast days must be an integer."
        )

    if not 1 <= days <= 7:
        raise ValueError(
            "Forecast days must be between 1 and 7."
        )

    config = load_config()

    config["forecast_days"] = days

    save_config(
        config
    )