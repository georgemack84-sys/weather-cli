import json
import time
from pathlib import Path


CACHE_DIRECTORY = Path.home() / ".weather-cli" / "cache"
DEFAULT_TTL_SECONDS = 600


def _cache_file(key):
    safe_key = (
        key.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    return CACHE_DIRECTORY / f"{safe_key}.json"


def load_cache(key, ttl_seconds=DEFAULT_TTL_SECONDS):
    path = _cache_file(key)

    if not path.exists():
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

    except (OSError, json.JSONDecodeError):
        return None

    timestamp = payload.get("timestamp")
    data = payload.get("data")

    if timestamp is None or data is None:
        return None

    age = time.time() - timestamp

    if age > ttl_seconds:
        return None

    return data


def save_cache(key, data):
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
    if not CACHE_DIRECTORY.exists():
        return

    for file in CACHE_DIRECTORY.glob("*.json"):
        try:
            file.unlink()
        except OSError:
            pass