import sys
from argparse import Namespace
from unittest.mock import patch

import pytest
import requests

from weather_cli import cli


def test_weather_parser_city():
    parser = cli.build_weather_parser()

    args = parser.parse_args(["Atlanta"])

    assert args.city == ["Atlanta"]
    assert args.forecast is False
    assert args.days is None
    assert args.metric is False
    assert args.imperial is False


def test_weather_parser_multiword_city():
    parser = cli.build_weather_parser()

    args = parser.parse_args(
        [
            "New",
            "York",
        ]
    )

    assert args.city == [
        "New",
        "York",
    ]


def test_weather_parser_forecast():
    parser = cli.build_weather_parser()

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
    parser = cli.build_weather_parser()

    args = parser.parse_args(
        [
            "London",
            "--metric",
        ]
    )

    assert args.metric is True
    assert args.imperial is False


def test_weather_parser_imperial():
    parser = cli.build_weather_parser()

    args = parser.parse_args(
        [
            "London",
            "--imperial",
        ]
    )

    assert args.metric is False
    assert args.imperial is True


def test_weather_parser_version(capsys):
    parser = cli.build_weather_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args(
            [
                "--version",
            ]
        )

    assert error.value.code == 0

    output = capsys.readouterr().out

    assert output.strip() == (
        f"weather {cli.__version__}"
    )


def test_config_set_city_parser():
    parser = cli.build_config_parser()

    args = parser.parse_args(
        [
            "set-city",
            "New",
            "York",
        ]
    )

    assert args.config_command == "set-city"
    assert args.default_city == [
        "New",
        "York",
    ]


def test_config_set_days_parser():
    parser = cli.build_config_parser()

    args = parser.parse_args(
        [
            "set-days",
            "5",
        ]
    )

    assert args.config_command == "set-days"
    assert args.forecast_days == 5


def test_config_set_units_parser():
    parser = cli.build_config_parser()

    args = parser.parse_args(
        [
            "set-units",
            "metric",
        ]
    )

    assert args.config_command == "set-units"
    assert args.units == "metric"


def test_config_show_parser():
    parser = cli.build_config_parser()

    args = parser.parse_args(
        [
            "show",
        ]
    )

    assert args.config_command == "show"


def test_config_clear_cache_parser():
    parser = cli.build_config_parser()

    args = parser.parse_args(
        [
            "clear-cache",
        ]
    )

    assert args.config_command == "clear-cache"


def test_config_parser_version(capsys):
    parser = cli.build_config_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args(
            [
                "--version",
            ]
        )

    assert error.value.code == 0

    output = capsys.readouterr().out

    assert output.strip() == (
        f"weather {cli.__version__}"
    )


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
    args = cli.parse_arguments()

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
    args = cli.parse_arguments()

    assert args.command == "weather"
    assert args.city == ["Atlanta"]
    assert args.forecast is True


@patch.object(
    sys,
    "argv",
    [
        "weather",
        "--version",
    ],
)
def test_parse_arguments_version(capsys):
    with pytest.raises(SystemExit) as error:
        cli.parse_arguments()

    assert error.value.code == 0

    output = capsys.readouterr().out

    assert output.strip() == (
        f"weather {cli.__version__}"
    )


@patch.object(
    sys,
    "argv",
    [
        "weather",
        "config",
        "--version",
    ],
)
def test_parse_arguments_config_version(capsys):
    with pytest.raises(SystemExit) as error:
        cli.parse_arguments()

    assert error.value.code == 0

    output = capsys.readouterr().out

    assert output.strip() == (
        f"weather {cli.__version__}"
    )


@patch("weather_cli.cli.load_config")
def test_resolve_preferences_uses_config(
    mock_load_config,
):
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

    city, metric, days = (
        cli.resolve_preferences(args)
    )

    assert city == "Atlanta"
    assert metric is False
    assert days == 3


@patch("weather_cli.cli.load_config")
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

    city, metric, days = (
        cli.resolve_preferences(args)
    )

    assert city == "London"
    assert metric is True
    assert days == 5


@patch("weather_cli.cli.load_config")
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

    city, metric, days = (
        cli.resolve_preferences(args)
    )

    assert city == "London"
    assert metric is False
    assert days == 5


def test_choose_location_empty_results():
    assert cli.choose_location([]) is None


def test_choose_location_single_result():
    location = {
        "name": "Atlanta",
        "state": "Georgia",
        "country": "United States",
        "timezone": "America/New_York",
    }

    assert (
        cli.choose_location(
            [location]
        )
        == location
    )


@patch.object(
    cli.console,
    "input",
    return_value="2",
)
def test_choose_location_multiple_results(
    mock_input,
):
    locations = [
        {
            "name": "Springfield",
            "state": "Illinois",
            "country": "United States",
            "timezone": "America/Chicago",
        },
        {
            "name": "Springfield",
            "state": "Missouri",
            "country": "United States",
            "timezone": "America/Chicago",
        },
    ]

    selected = cli.choose_location(
        locations
    )

    assert selected == locations[1]

    mock_input.assert_called_once()


@patch.object(
    cli.console,
    "input",
    return_value="q",
)
def test_choose_location_cancel(
    mock_input,
):
    locations = [
        {
            "name": "Springfield",
            "state": "Illinois",
            "country": "United States",
        },
        {
            "name": "Springfield",
            "state": "Missouri",
            "country": "United States",
        },
    ]

    result = cli.choose_location(
        locations
    )

    assert result is None

    mock_input.assert_called_once()


@patch.object(
    cli.console,
    "input",
    side_effect=[
        "x",
        "99",
        "1",
    ],
)
def test_choose_location_retries_invalid_input(
    mock_input,
):
    locations = [
        {
            "name": "Atlanta",
            "state": "Georgia",
            "country": "United States",
        },
        {
            "name": "London",
            "state": "",
            "country": "United Kingdom",
        },
    ]

    selected = cli.choose_location(
        locations
    )

    assert selected == locations[0]
    assert mock_input.call_count == 3


@patch("weather_cli.cli.load_config")
def test_display_configuration(
    mock_load_config,
    capsys,
):
    mock_load_config.return_value = {
        "default_city": "Atlanta",
        "metric": False,
        "forecast_days": 5,
    }

    cli.display_configuration()

    output = (
        capsys.readouterr().out
    )

    assert (
        "Weather CLI Configuration"
        in output
    )
    assert "Atlanta" in output
    assert "imperial" in output
    assert "5" in output


@patch("weather_cli.cli.load_config")
def test_display_configuration_without_default_city(
    mock_load_config,
    capsys,
):
    mock_load_config.return_value = {
        "default_city": None,
        "metric": True,
        "forecast_days": 3,
    }

    cli.display_configuration()

    output = (
        capsys.readouterr().out
    )

    assert "Not configured" in output
    assert "metric" in output


@patch(
    "weather_cli.cli.set_default_city"
)
def test_handle_config_set_city(
    mock_set_default_city,
):
    args = Namespace(
        config_command="set-city",
        default_city=[
            "New",
            "York",
        ],
    )

    cli.handle_config(args)

    mock_set_default_city.assert_called_once_with(
        "New York"
    )


@patch(
    "weather_cli.cli.set_forecast_days"
)
def test_handle_config_set_days(
    mock_set_forecast_days,
):
    args = Namespace(
        config_command="set-days",
        forecast_days=5,
    )

    cli.handle_config(args)

    mock_set_forecast_days.assert_called_once_with(
        5
    )


@patch(
    "weather_cli.cli.set_forecast_days",
    side_effect=ValueError(
        "Forecast days must be between 1 and 7."
    ),
)
def test_handle_config_invalid_days(
    mock_set_forecast_days,
):
    args = Namespace(
        config_command="set-days",
        forecast_days=10,
    )

    cli.handle_config(args)

    mock_set_forecast_days.assert_called_once_with(
        10
    )


@patch(
    "weather_cli.cli.set_metric"
)
def test_handle_config_metric(
    mock_set_metric,
):
    args = Namespace(
        config_command="set-units",
        units="metric",
    )

    cli.handle_config(args)

    mock_set_metric.assert_called_once_with(
        True
    )


@patch(
    "weather_cli.cli.set_metric"
)
def test_handle_config_imperial(
    mock_set_metric,
):
    args = Namespace(
        config_command="set-units",
        units="imperial",
    )

    cli.handle_config(args)

    mock_set_metric.assert_called_once_with(
        False
    )


@patch(
    "weather_cli.cli.display_configuration"
)
def test_handle_config_show(
    mock_display_configuration,
):
    args = Namespace(
        config_command="show",
    )

    cli.handle_config(args)

    mock_display_configuration.assert_called_once()


@patch(
    "weather_cli.cli.clear_cache"
)
def test_handle_config_clear_cache(
    mock_clear_cache,
):
    args = Namespace(
        config_command="clear-cache",
    )

    cli.handle_config(args)

    mock_clear_cache.assert_called_once()


def test_handle_config_without_subcommand(
    capsys,
):
    args = Namespace(
        config_command=None,
    )

    cli.handle_config(args)

    output = (
        capsys.readouterr().out
    )

    assert (
        "weather config --help"
        in output
    )


@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_without_city(
    mock_resolve_preferences,
    capsys,
):
    mock_resolve_preferences.return_value = (
        None,
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert (
        "No city specified"
        in output
    )


@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_invalid_days(
    mock_resolve_preferences,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        10,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert (
        "between 1 and 7"
        in output
    )


@patch(
    "weather_cli.cli.search_locations",
    return_value=[],
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_no_locations(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "NotARealCity",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Could not find" in output

    mock_search_locations.assert_called_once_with(
        "NotARealCity"
    )


@patch(
    "weather_cli.cli.choose_location",
    return_value=None,
)
@patch(
    "weather_cli.cli.search_locations"
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_cancelled(
    mock_resolve_preferences,
    mock_search_locations,
    mock_choose_location,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Springfield",
        False,
        3,
    )

    mock_search_locations.return_value = [
        {
            "name": "Springfield",
            "latitude": 1.0,
            "longitude": 2.0,
            "state": "Illinois",
            "country": "United States",
            "timezone": "America/Chicago",
        }
    ]

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Search cancelled" in output

    mock_choose_location.assert_called_once()


@patch(
    "weather_cli.cli.display_current_weather"
)
@patch(
    "weather_cli.cli.get_weather"
)
@patch(
    "weather_cli.cli.choose_location"
)
@patch(
    "weather_cli.cli.search_locations"
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_success_current_only(
    mock_resolve_preferences,
    mock_search_locations,
    mock_choose_location,
    mock_get_weather,
    mock_display_current_weather,
):
    location = {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "state": "Georgia",
        "country": "United States",
        "timezone": "America/New_York",
    }

    weather = {
        "current": {
            "temperature_2m": 82.0,
        }
    }

    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    mock_search_locations.return_value = [
        location
    ]

    mock_choose_location.return_value = (
        location
    )

    mock_get_weather.return_value = (
        weather
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    mock_get_weather.assert_called_once_with(
        33.749,
        -84.388,
        3,
        False,
    )

    mock_display_current_weather.assert_called_once_with(
        location,
        weather,
        False,
    )


@patch(
    "weather_cli.cli.display_forecast"
)
@patch(
    "weather_cli.cli.display_current_weather"
)
@patch(
    "weather_cli.cli.get_weather"
)
@patch(
    "weather_cli.cli.choose_location"
)
@patch(
    "weather_cli.cli.search_locations"
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_success_with_forecast(
    mock_resolve_preferences,
    mock_search_locations,
    mock_choose_location,
    mock_get_weather,
    mock_display_current_weather,
    mock_display_forecast,
):
    location = {
        "name": "Atlanta",
        "latitude": 33.749,
        "longitude": -84.388,
        "state": "Georgia",
        "country": "United States",
        "timezone": "America/New_York",
    }

    weather = {
        "current": {},
        "daily": {},
    }

    mock_resolve_preferences.return_value = (
        "Atlanta",
        True,
        5,
    )

    mock_search_locations.return_value = [
        location
    ]

    mock_choose_location.return_value = (
        location
    )

    mock_get_weather.return_value = (
        weather
    )

    args = Namespace(
        forecast=True,
    )

    cli.run_weather(args)

    mock_display_current_weather.assert_called_once_with(
        location,
        weather,
        True,
    )

    mock_display_forecast.assert_called_once_with(
        weather,
        True,
    )


@patch(
    "weather_cli.cli.search_locations",
    side_effect=requests.exceptions.Timeout,
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_timeout(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "timed out" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=(
        requests.exceptions.ConnectionError
    ),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_connection_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Unable to connect" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=requests.exceptions.HTTPError(
        "500"
    ),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_http_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "HTTP error" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=(
        requests.exceptions.RequestException(
            "request failed"
        )
    ),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_request_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Request error" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=KeyError("missing"),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_key_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "unexpected data" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=ValueError(
        "bad data"
    ),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_value_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Data error" in output


@patch(
    "weather_cli.cli.search_locations",
    side_effect=RuntimeError(
        "unexpected"
    ),
)
@patch(
    "weather_cli.cli.resolve_preferences"
)
def test_run_weather_unexpected_error(
    mock_resolve_preferences,
    mock_search_locations,
    capsys,
):
    mock_resolve_preferences.return_value = (
        "Atlanta",
        False,
        3,
    )

    args = Namespace(
        forecast=False,
    )

    cli.run_weather(args)

    output = (
        capsys.readouterr().out
    )

    assert "Unexpected error" in output


@patch(
    "weather_cli.cli.run_weather"
)
@patch(
    "weather_cli.cli.parse_arguments"
)
@patch(
    "weather_cli.cli.configure_logging"
)
def test_main_weather(
    mock_configure_logging,
    mock_parse_arguments,
    mock_run_weather,
):
    args = Namespace(
        command="weather",
    )

    mock_parse_arguments.return_value = (
        args
    )

    cli.main()

    mock_configure_logging.assert_called_once()

    mock_run_weather.assert_called_once_with(
        args
    )


@patch(
    "weather_cli.cli.handle_config"
)
@patch(
    "weather_cli.cli.parse_arguments"
)
@patch(
    "weather_cli.cli.configure_logging"
)
def test_main_config(
    mock_configure_logging,
    mock_parse_arguments,
    mock_handle_config,
):
    args = Namespace(
        command="config",
    )

    mock_parse_arguments.return_value = (
        args
    )

    cli.main()

    mock_configure_logging.assert_called_once()

    mock_handle_config.assert_called_once_with(
        args
    )