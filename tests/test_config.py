import json

import pytest

from weather_cli import config


def test_load_config_returns_defaults_when_file_missing(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    result = config.load_config()

    assert result == {
        "default_city": None,
        "metric": False,
        "forecast_days": 3,
    }


def test_save_and_load_config(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    data = {
        "default_city": "Atlanta",
        "metric": False,
        "forecast_days": 5,
    }

    config.save_config(data)

    assert config_file.exists()

    loaded = config.load_config()

    assert loaded == data


def test_load_config_merges_partial_config(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    app_directory.mkdir()

    config_file.write_text(
        json.dumps(
            {
                "default_city": "London",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    loaded = config.load_config()

    assert loaded["default_city"] == "London"
    assert loaded["metric"] is False
    assert loaded["forecast_days"] == 3


def test_load_config_ignores_unknown_keys(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    app_directory.mkdir()

    config_file.write_text(
        json.dumps(
            {
                "default_city": "Atlanta",
                "unknown_setting": "ignored",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    loaded = config.load_config()

    assert loaded["default_city"] == "Atlanta"
    assert "unknown_setting" not in loaded


def test_load_config_returns_defaults_for_invalid_json(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    app_directory.mkdir()

    config_file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    loaded = config.load_config()

    assert loaded == config.DEFAULT_CONFIG


def test_load_config_returns_defaults_for_non_dictionary_json(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    app_directory.mkdir()

    config_file.write_text(
        json.dumps(
            [
                "not",
                "a",
                "dictionary",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    loaded = config.load_config()

    assert loaded == config.DEFAULT_CONFIG


def test_set_default_city(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_default_city("Atlanta")

    loaded = config.load_config()

    assert loaded["default_city"] == "Atlanta"


def test_set_default_city_strips_whitespace(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_default_city("  New York  ")

    loaded = config.load_config()

    assert loaded["default_city"] == "New York"


def test_empty_city_clears_default(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_default_city("Atlanta")

    config.set_default_city("   ")

    loaded = config.load_config()

    assert loaded["default_city"] is None


def test_none_city_clears_default(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_default_city("Atlanta")

    config.set_default_city(None)

    loaded = config.load_config()

    assert loaded["default_city"] is None


def test_set_metric_true(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_metric(True)

    loaded = config.load_config()

    assert loaded["metric"] is True


def test_set_metric_false(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_metric(False)

    loaded = config.load_config()

    assert loaded["metric"] is False


def test_set_forecast_days(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_forecast_days(5)

    loaded = config.load_config()

    assert loaded["forecast_days"] == 5


def test_set_forecast_days_minimum(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_forecast_days(1)

    loaded = config.load_config()

    assert loaded["forecast_days"] == 1


def test_set_forecast_days_maximum(
    tmp_path,
    monkeypatch,
):
    app_directory = tmp_path / ".weather-cli"
    config_file = app_directory / "config.json"

    monkeypatch.setattr(
        config,
        "APP_DIRECTORY",
        app_directory,
    )

    monkeypatch.setattr(
        config,
        "CONFIG_FILE",
        config_file,
    )

    config.set_forecast_days(7)

    loaded = config.load_config()

    assert loaded["forecast_days"] == 7


@pytest.mark.parametrize(
    "days",
    [
        0,
        8,
        -1,
        100,
    ],
)
def test_set_forecast_days_rejects_out_of_range(days):
    with pytest.raises(
        ValueError,
        match="between 1 and 7",
    ):
        config.set_forecast_days(days)


def test_set_forecast_days_rejects_non_integer():
    with pytest.raises(
        TypeError,
        match="must be an integer",
    ):
        config.set_forecast_days("5")
