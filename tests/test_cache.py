import json
import time
from unittest.mock import patch

from weather_cli import cache


def configure_test_cache(tmp_path, monkeypatch):
    cache_directory = tmp_path / "cache"

    monkeypatch.setattr(
        cache,
        "CACHE_DIRECTORY",
        cache_directory,
    )

    return cache_directory


def test_cache_file_builds_json_path(tmp_path, monkeypatch):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    path = cache._cache_file("atlanta")

    assert path == cache_directory / "atlanta.json"


def test_cache_file_sanitizes_unsafe_characters(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    path = cache._cache_file('New York/GA\\test:weather?*"< >|')

    assert path.parent == cache_directory
    assert path.suffix == ".json"

    assert "/" not in path.name
    assert "\\" not in path.name
    assert ":" not in path.name
    assert "?" not in path.name
    assert "*" not in path.name
    assert '"' not in path.name
    assert "<" not in path.name
    assert ">" not in path.name
    assert "|" not in path.name
    assert " " not in path.name


def test_save_and_load_cache(
    tmp_path,
    monkeypatch,
):
    configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    data = {
        "temperature": 82.0,
        "weather_code": 2,
    }

    with patch(
        "weather_cli.cache.time.time",
        return_value=1000.0,
    ):
        cache.save_cache(
            "atlanta",
            data,
        )

    with patch(
        "weather_cli.cache.time.time",
        return_value=1050.0,
    ):
        loaded = cache.load_cache(
            "atlanta",
            ttl_seconds=600,
        )

    assert loaded == data


def test_save_cache_creates_directory(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    assert not cache_directory.exists()

    cache.save_cache(
        "atlanta",
        {
            "temperature": 82.0,
        },
    )

    assert cache_directory.exists()
    assert (cache_directory / "atlanta.json").exists()


def test_save_cache_writes_timestamp_and_data(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    data = {
        "temperature": 82.0,
    }

    with patch(
        "weather_cli.cache.time.time",
        return_value=1234.5,
    ):
        cache.save_cache(
            "atlanta",
            data,
        )

    path = cache_directory / "atlanta.json"

    payload = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    assert payload == {
        "timestamp": 1234.5,
        "data": data,
    }


def test_missing_cache_returns_none(
    tmp_path,
    monkeypatch,
):
    configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    result = cache.load_cache("missing")

    assert result is None


def test_expired_cache_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            {
                "timestamp": 1000.0,
                "data": {
                    "temperature": 82.0,
                },
            }
        ),
        encoding="utf-8",
    )

    with patch(
        "weather_cli.cache.time.time",
        return_value=2000.0,
    ):
        result = cache.load_cache(
            "atlanta",
            ttl_seconds=600,
        )

    assert result is None
    assert not path.exists()


def test_expired_cache_unlink_failure_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            {
                "timestamp": 1000.0,
                "data": {
                    "temperature": 82.0,
                },
            }
        ),
        encoding="utf-8",
    )

    with (
        patch(
            "weather_cli.cache.time.time",
            return_value=2000.0,
        ),
        patch.object(
            type(path),
            "unlink",
            side_effect=OSError("cannot delete"),
        ),
    ):
        result = cache.load_cache(
            "atlanta",
            ttl_seconds=600,
        )

    assert result is None


def test_invalid_json_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    assert cache.load_cache("atlanta") is None


def test_non_dictionary_payload_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            [
                "invalid",
                "payload",
            ]
        ),
        encoding="utf-8",
    )

    assert cache.load_cache("atlanta") is None


def test_missing_timestamp_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            {
                "data": {
                    "temperature": 82.0,
                }
            }
        ),
        encoding="utf-8",
    )

    assert cache.load_cache("atlanta") is None


def test_missing_data_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            {
                "timestamp": time.time(),
            }
        ),
        encoding="utf-8",
    )

    assert cache.load_cache("atlanta") is None


def test_invalid_timestamp_returns_none(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "atlanta.json"

    path.write_text(
        json.dumps(
            {
                "timestamp": "invalid",
                "data": {
                    "temperature": 82.0,
                },
            }
        ),
        encoding="utf-8",
    )

    assert cache.load_cache("atlanta") is None


def test_clear_cache(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    first = cache_directory / "first.json"

    second = cache_directory / "second.json"

    first.write_text(
        "{}",
        encoding="utf-8",
    )

    second.write_text(
        "{}",
        encoding="utf-8",
    )

    cache.clear_cache()

    assert not first.exists()
    assert not second.exists()


def test_clear_cache_when_directory_missing(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    assert not cache_directory.exists()

    cache.clear_cache()

    assert not cache_directory.exists()


def test_clear_cache_ignores_non_json_files(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    json_file = cache_directory / "weather.json"

    text_file = cache_directory / "keep.txt"

    json_file.write_text(
        "{}",
        encoding="utf-8",
    )

    text_file.write_text(
        "keep me",
        encoding="utf-8",
    )

    cache.clear_cache()

    assert not json_file.exists()
    assert text_file.exists()


def test_clear_cache_ignores_unlink_failure(
    tmp_path,
    monkeypatch,
):
    cache_directory = configure_test_cache(
        tmp_path,
        monkeypatch,
    )

    cache_directory.mkdir(
        parents=True,
    )

    path = cache_directory / "weather.json"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    with patch.object(
        type(path),
        "unlink",
        side_effect=OSError("cannot delete"),
    ):
        cache.clear_cache()
