import sys
from argparse import Namespace
from unittest.mock import patch

from weather_cli.cli import (
    build_config_parser,
    build_weather_parser,
    parse_arguments,
    resolve_preferences,
)


def test_weather_parser_city():
    parser = build_weather_parser()

    args = parser.parse_args(["Atlanta"])

    assert args.city == ["Atlanta"]
    assert args.forecast is False
    assert args.days is None
    assert args.metric is False
    assert args.imperial is False


def test_weather_parser_multiword_city():
    parser = build_weather_parser()

    args = parser.parse_args(["New", "York"])

    assert args.city == ["New", "York"]


def test_weather_parser_forecast():
    parser = build_weather_parser()

    args = parser.parse_args(
        [
            "Atlanta",
            "--forecast",
            "--days",
            "5",
        ]
    )

    assert args.city == ["Atlanta"]
    assert args.forecast is True
    assert args.days == 5


def test_weather_parser_metric():
    parser = build_weather_parser()

    args = parser.parse_args(
        [
            "London",
            "--metric",
        ]
    )

    assert args.metric is True
    assert args.imperial is False


def test_weather_parser_imperial():
    parser = build_weather_parser()

    args = parser.parse_args(
        [
            "London",
            "--imperial",
        ]
    )

    assert args.metric is False
    assert args.imperial is True


def test_config_set_city_parser():
    parser = build_config_parser()

    args = parser.parse_args(
        [
            "set-city",
            "New",
            "York",
        ]
    )

    assert args.config_command == "set-city"
    assert args.default_city == ["New", "York"]


def test_config_set_days_parser():
    parser = build_config_parser()

    args = parser.parse_args(
        [
            "set-days",
            "5",
        ]
    )

    assert args.config_command == "set-days"
    assert args.forecast_days == 5


def test_config_set_units_parser():
    parser = build_config_parser()

    args = parser.parse_args(
        [
            "set-units",
            "metric",
        ]
    )

    assert args.config_command == "set-units"
    assert args.units == "metric"


def test_config_show_parser():
    parser = build_config_parser()

    args = parser.parse_args(["show"])

    assert args.config_command == "show"


@patch.object(
    sys,
    "argv",
    [
        "weather",
        "config",
        "set-city",
        "Atlanta",
    ],
)
def test_parse_arguments_config():
    args = parse_arguments()

    assert args.command == "config"
    assert args.config_command == "set-city"
    assert args.default_city == ["Atlanta"]


@patch.object(
    sys,
    "argv",
    [
        "weather",
        "Atlanta",
        "--forecast",
    ],
)
def test_parse_arguments_weather():
    args = parse_arguments()

    assert args.command == "weather"
    assert args.city == ["Atlanta"]
    assert args.forecast is True


@patch(
    "weather_cli.cli.load_config"
)
def test_resolve_preferences_uses_config(mock_load_config):
    mock_load_config.return_value = {
        "default_city": "Atlanta",
        "metric": False,
        "forecast_days": 3,
    }

    args = Namespace(
        city=[],
        metric=False,
        imperial=False,
        days=None,
    )

    city, metric, days = resolve_preferences(args)

    assert city == "Atlanta"
    assert metric is False
    assert days == 3


@patch(
    "weather_cli.cli.load_config"
)
def test_resolve_preferences_cli_overrides_config(
    mock_load_config,
):
    mock_load_config.return_value = {
        "default_city": "Atlanta",
        "metric": False,
        "forecast_days": 3,
    }

    args = Namespace(
        city=["London"],
        metric=True,
        imperial=False,
        days=5,
    )

    city, metric, days = resolve_preferences(args)

    assert city == "London"
    assert metric is True
    assert days == 5


@patch(
    "weather_cli.cli.load_config"
)
def test_resolve_preferences_imperial_override(
    mock_load_config,
):
    mock_load_config.return_value = {
        "default_city": "London",
        "metric": True,
        "forecast_days": 5,
    }

    args = Namespace(
        city=[],
        metric=False,
        imperial=True,
        days=None,
    )

    city, metric, days = resolve_preferences(args)

    assert city == "London"
    assert metric is False
    assert days == 5