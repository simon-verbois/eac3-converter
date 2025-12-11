import glob
import logging
import os
import signal
import sys
import time

# Import from current package
from .cache_manager import CacheManager
from .config import config, INPUT_DIR, CACHE_FILE
from .logging_config import setup_logging
from .audio_processor import AudioProcessor
from .file_processor import FileProcessor
from .scheduler import Scheduler

logger = logging.getLogger("eac3_converter")

# Global cache manager for signal handler
cache_manager = None

def cleanup_temp_files(input_dir: str) -> int:
    """Clean up temporary .temp_* files from previous runs recursively."""
    cleaned_count = 0

    # Walk through all directories recursively
    for root, dirs, files in os.walk(input_dir):
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
    """Handle shutdown signals to save cache and cleanup temp files."""
    logger.info(f"Received signal {signum}, saving cache and cleaning up...")
    if cache_manager:
        cache_manager.save_cache()

    # Clean up any remaining temp files
    cleanup_temp_files(INPUT_DIR)

    sys.exit(0)

def setup_timezone():
    """Set system timezone from configuration."""
    timezone = config.system.timezone
    timezone_path = f"/usr/share/zoneinfo/{timezone}"
    if os.path.exists("/etc/localtime") or os.path.islink("/etc/localtime"):
        os.remove("/etc/localtime")
    os.symlink(timezone_path, "/etc/localtime")
    with open("/etc/timezone", "w") as f:
        f.write(timezone)
    os.environ['TZ'] = timezone
    time.tzset()

def main():
    """Main application entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Set up timezone
    setup_timezone()

    # Set up logging
    setup_logging()

    # Clean up any leftover temporary files from previous runs
    cleanup_temp_files(INPUT_DIR)

    # Initialize components
    global cache_manager
    cache_manager = CacheManager(CACHE_FILE)
    cache_manager.load_cache()

    audio_processor = AudioProcessor(config.app.debug_mode)
    file_processor = FileProcessor(cache_manager, audio_processor)
    scheduler = Scheduler(file_processor)

    # Start the scheduler
    scheduler.run()

if __name__ == "__main__":
    main()
