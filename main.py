import glob
import logging
import os
import signal
import sys
import time

# Import from src package
from src.cache_manager import CacheManager
from src.config import config, INPUT_DIR, CACHE_FILE
from src.logging_config import setup_logging
from src.audio_processor import AudioProcessor
from src.file_processor import FileProcessor
from src.scheduler import Scheduler

logger = logging.getLogger("eac3_converter")

# Global cache manager for signal handler
cache_manager = None

def cleanup_temp_files(input_dir: str) -> int:
    """Clean up temporary .temp_* files from previous runs."""
    temp_pattern = os.path.join(input_dir, ".temp_*")
    temp_files = glob.glob(temp_pattern)

    cleaned_count = 0
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            logger.info(f"Cleaned up temporary file: {temp_file}")
            cleaned_count += 1
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {temp_file}: {e}")

    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} temporary files")

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
    timezone = config.timezone
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

    audio_processor = AudioProcessor(config.debug_mode)
    file_processor = FileProcessor(cache_manager, audio_processor)
    scheduler = Scheduler(file_processor)

    # Start the scheduler
    scheduler.run()

if __name__ == "__main__":
    main()
