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
    """Load configuration from disk."""

    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            saved_config = json.load(file)

    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG.copy()
    config.update(saved_config)

    return config


def save_config(config):
    """Save configuration to disk."""

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
    """Set the user's default city."""

    config = load_config()

    config["default_city"] = city

    save_config(config)


def set_metric(metric):
    """Set the user's preferred unit system."""

    config = load_config()

    config["metric"] = metric

    save_config(config)


def set_forecast_days(days):
    """Set the default forecast length."""

    if not 1 <= days <= 7:
        raise ValueError(
            "Forecast days must be between 1 and 7."
        )

    config = load_config()

    config["forecast_days"] = days

    save_config(config)