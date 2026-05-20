import logging
import os
import signal
import sys
import time

from .cache_manager import CacheManager
from .config import config, INPUT_DIR, CACHE_DB
from .exceptions import ConfigError
from .logging_config import setup_logging
from .audio_processor import AudioProcessor
from .file_processor import FileProcessor
from .scheduler import Scheduler

logger = logging.getLogger("eac3_converter")

cache_manager: CacheManager | None = None


def cleanup_temp_files(input_dir: str) -> int:
    """Clean up temporary .temp_* files from previous runs recursively."""
    cleaned_count = 0
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.startswith(".temp_"):
                temp_file_path = os.path.join(root, file)
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file_path}: {e}")

    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} temporary files from previous runs")

    return cleaned_count


def signal_handler(signum, frame):
    """Handle shutdown signals to close cache and cleanup temp files."""
    logger.info(f"Received signal {signum}, closing cache and cleaning up...")
    if cache_manager is not None:
        cache_manager.close()
    cleanup_temp_files(INPUT_DIR)
    sys.exit(0)


def setup_timezone():
    """Apply timezone from TZ env var using Python's time module.

    We rely on the TZ env var (already set by Docker/K8s in most setups) and
    time.tzset() to make Python use it. We do NOT touch /etc/localtime — that
    requires root and would crash outside a container.
    """
    tz = config.tz
    os.environ['TZ'] = tz
    try:
        time.tzset()
    except AttributeError:
        logger.warning("time.tzset() unavailable on this platform; TZ may be ignored")


def main():
    """Main application entry point."""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    setup_timezone()
    setup_logging()

    cleanup_temp_files(INPUT_DIR)

    global cache_manager
    cache_manager = CacheManager(CACHE_DB)

    audio_processor = AudioProcessor(config.app.debug_mode)
    file_processor = FileProcessor(cache_manager, audio_processor)
    scheduler = Scheduler(file_processor)

    try:
        scheduler.run()
    finally:
        cache_manager.close()


if __name__ == "__main__":
    try:
        main()
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
