import time

from weather_cli import cache


def test_save_and_load_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cache,
        "CACHE_DIRECTORY",
        tmp_path,
    )

    cache.save_cache(
        "test-key",
        {"temperature": 72},
    )

    result = cache.load_cache(
        "test-key"
    )

    assert result == {
        "temperature": 72
    }


def test_expired_cache_returns_none(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        cache,
        "CACHE_DIRECTORY",
        tmp_path,
    )

    cache.save_cache(
        "expired",
        {"temperature": 72},
    )

    result = cache.load_cache(
        "expired",
        ttl_seconds=-1,
    )

    assert result is None


def test_missing_cache_returns_none(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        cache,
        "CACHE_DIRECTORY",
        tmp_path,
    )

    result = cache.load_cache(
        "does-not-exist"
    )

    assert result is None


def test_clear_cache(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        cache,
        "CACHE_DIRECTORY",
        tmp_path,
    )

    cache.save_cache(
        "one",
        {"value": 1},
    )

    cache.save_cache(
        "two",
        {"value": 2},
    )

    cache.clear_cache()

    assert list(
        tmp_path.glob("*.json")
    ) == []