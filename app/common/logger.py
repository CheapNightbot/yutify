import logging
import logging.handlers

logging.basicConfig(
    format="[{asctime}] [{levelname}] {filename}: {message}",
    datefmt="%Y, %b %d ~ %I:%M:%S %p",
    style="{",
    level=logging.INFO,
    encoding="utf-8"
)

logger = logging.getLogger(__name__)
