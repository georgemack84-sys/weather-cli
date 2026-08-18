from pathlib import Path
from unittest.mock import patch

from weather_cli import logging_config


def test_configure_logging_creates_log_directory(
    tmp_path,
    monkeypatch,
):
    log_directory = tmp_path / "logs"
    log_file = log_directory / "weather-cli.log"

    monkeypatch.setattr(
        logging_config,
        "LOG_DIRECTORY",
        log_directory,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_FILE",
        log_file,
    )

    assert not log_directory.exists()

    with patch("weather_cli.logging_config.logging.basicConfig") as mock_basic_config:
        logging_config.configure_logging()

    assert log_directory.exists()

    mock_basic_config.assert_called_once()


def test_configure_logging_uses_log_file(
    tmp_path,
    monkeypatch,
):
    log_directory = tmp_path / "logs"
    log_file = log_directory / "weather-cli.log"

    monkeypatch.setattr(
        logging_config,
        "LOG_DIRECTORY",
        log_directory,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_FILE",
        log_file,
    )

    with patch("weather_cli.logging_config.logging.basicConfig") as mock_basic_config:
        logging_config.configure_logging()

    _, kwargs = mock_basic_config.call_args

    assert Path(kwargs["filename"]) == log_file


def test_configure_logging_sets_expected_level(
    tmp_path,
    monkeypatch,
):
    log_directory = tmp_path / "logs"
    log_file = log_directory / "weather-cli.log"

    monkeypatch.setattr(
        logging_config,
        "LOG_DIRECTORY",
        log_directory,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_FILE",
        log_file,
    )

    with patch("weather_cli.logging_config.logging.basicConfig") as mock_basic_config:
        logging_config.configure_logging()

    _, kwargs = mock_basic_config.call_args

    assert kwargs["level"] == logging_config.logging.INFO


def test_configure_logging_sets_format(
    tmp_path,
    monkeypatch,
):
    log_directory = tmp_path / "logs"
    log_file = log_directory / "weather-cli.log"

    monkeypatch.setattr(
        logging_config,
        "LOG_DIRECTORY",
        log_directory,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_FILE",
        log_file,
    )

    with patch("weather_cli.logging_config.logging.basicConfig") as mock_basic_config:
        logging_config.configure_logging()

    _, kwargs = mock_basic_config.call_args

    assert "format" in kwargs
    assert kwargs["format"]


def test_configure_logging_directory_creation_is_idempotent(
    tmp_path,
    monkeypatch,
):
    log_directory = tmp_path / "logs"
    log_file = log_directory / "weather-cli.log"

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_DIRECTORY",
        log_directory,
    )

    monkeypatch.setattr(
        logging_config,
        "LOG_FILE",
        log_file,
    )

    with patch("weather_cli.logging_config.logging.basicConfig") as mock_basic_config:
        logging_config.configure_logging()

    assert log_directory.exists()

    mock_basic_config.assert_called_once()
