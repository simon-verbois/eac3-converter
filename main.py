import os
import time
import sys

# Import from src package
from src.config import config
from src.logging_config import setup_logging
from src.cache_manager import CacheManager
from src.audio_processor import AudioProcessor
from src.file_processor import FileProcessor
from src.scheduler import Scheduler

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
    # Set up timezone
    setup_timezone()

    # Set up logging
    setup_logging()

    # Initialize components
    cache_manager = CacheManager(config.cache_file)
    cache_manager.load_cache()

    audio_processor = AudioProcessor(config.debug_mode)
    file_processor = FileProcessor(cache_manager, audio_processor)
    scheduler = Scheduler(file_processor)

    # Start the scheduler
    scheduler.run()

if __name__ == "__main__":
    main()
