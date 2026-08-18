import logging
from pathlib import Path

LOG_DIRECTORY = Path.home() / ".weather-cli" / "logs"
LOG_FILE = LOG_DIRECTORY / "weather-cli.log"


def configure_logging():
    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        encoding="utf-8",
    )
