import json
import time
from pathlib import Path

CACHE_DIRECTORY = Path.home() / ".weather-cli" / "cache"
DEFAULT_TTL_SECONDS = 600


def _cache_file(key):
    """
    Build a safe cache-file path from a cache key.
    """

    safe_key = str(key)

    for character in (
        " ",
        "/",
        "\\",
        ":",
        "?",
        "*",
        '"',
        "<",
        ">",
        "|",
    ):
        safe_key = safe_key.replace(
            character,
            "_",
        )

    return CACHE_DIRECTORY / f"{safe_key}.json"


def load_cache(
    key,
    ttl_seconds=DEFAULT_TTL_SECONDS,
):
    """
    Load cached data if it exists and has not expired.

    Return None when the cache is missing, malformed,
    unreadable, incomplete, invalid, or expired.
    """

    path = _cache_file(key)

    if not path.exists():
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None

    if not isinstance(payload, dict):
        return None

    timestamp = payload.get("timestamp")

    if timestamp is None:
        return None

    if "data" not in payload:
        return None

    data = payload["data"]

    if not isinstance(
        timestamp,
        (
            int,
            float,
        ),
    ):
        return None

    age = time.time() - timestamp

    if age > ttl_seconds:
        try:
            path.unlink()
        except OSError:
            pass

        return None

    return data


def save_cache(
    key,
    data,
):
    """
    Save data to the Weather CLI cache.
    """

    CACHE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "timestamp": time.time(),
        "data": data,
    }

    path = _cache_file(key)

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
        )


def clear_cache():
    """
    Remove all JSON files from the Weather CLI cache.

    Missing directories and individual deletion failures
    are ignored so cache cleanup cannot break the CLI.
    """

    if not CACHE_DIRECTORY.exists():
        return

    for file in CACHE_DIRECTORY.glob("*.json"):
        try:
            file.unlink()
        except OSError:
            pass
