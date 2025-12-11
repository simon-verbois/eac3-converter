import logging
import os
import time
from datetime import datetime, date, timedelta

from .config import config, INPUT_DIR
from .file_processor import FileProcessor

logger = logging.getLogger("eac3_converter")


class Scheduler:
    """Handles the scheduling and main processing loop."""

    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
        self.start_hour, self.start_minute = config.get_parsed_start_time()
        self.run_immediately = config.schedule.run_immediately
        self.input_dir = INPUT_DIR
        self.last_run_date: date | None = None

    def should_run_now(self) -> bool:
        """Determine if processing should run at the current time."""
        now = datetime.now()

        if self.run_immediately:
            logger.info("RUN_IMMEDIATELY is enabled. Processing files regardless of schedule.")
            return True

        if (now.hour > self.start_hour or
            (now.hour == self.start_hour and now.minute >= self.start_minute)) and \
           (self.last_run_date is None or self.last_run_date < now.date()):
            logger.info(f"Current time {now.hour}:{now.minute:02d} is after start time "
                       f"{self.start_hour}:{self.start_minute:02d}. Starting daily file processing...")
            self.last_run_date = now.date()
            return True

        logger.debug(f"Schedule check: current={now.hour}:{now.minute:02d}, "
                    f"start={self.start_hour}:{self.start_minute:02d}, last_run={self.last_run_date}")
        return False

    def process_files(self) -> None:
        """Process all MKV files in the input directory."""
        files_to_process = self.file_processor.find_mkv_files(self.input_dir)

        logger.debug(f"Total files to process: {len(files_to_process)}")

        processed_count = 0
        for file_path in files_to_process:
            self.file_processor.process_file(file_path)
            processed_count += 1

        # Get cache size for summary
        cache_size = self.file_processor.cache_manager.get_cache_size()

        logger.info(f"Processing summary: {processed_count} files processed, "
                   f"{cache_size} total cached entries")

        if not self.run_immediately:
            logger.info("Finishing daily processing...")

    def calculate_wait_seconds(self) -> int:
        """Calculate seconds to wait until start time."""
        now = datetime.now()
        start_time_today = now.replace(hour=self.start_hour, minute=self.start_minute, second=0, microsecond=0)

        if now < start_time_today:
            # Wait until start time today
            wait_seconds = int((start_time_today - now).total_seconds())
        else:
            # Start time has passed today, wait until tomorrow
            tomorrow = now + timedelta(days=1)
            start_time_tomorrow = tomorrow.replace(hour=self.start_hour, minute=self.start_minute, second=0, microsecond=0)
            wait_seconds = int((start_time_tomorrow - now).total_seconds())

        return wait_seconds

    def run(self) -> None:
        """Main processing loop - waits precisely until next execution time."""
        logger.info("Starting watch service...")
        logger.debug(f"Configuration: INPUT_DIR={self.input_dir}, "
                    f"START_TIME={self.start_hour}:{self.start_minute:02d}, "
                    f"RUN_IMMEDIATELY={self.run_immediately}")

        while True:
            if self.run_immediately:
                # For immediate runs, process once and exit
                logger.info("RUN_IMMEDIATELY is enabled. Processing files once and exiting.")
                self.process_files()
                break

            # Calculate wait time until next execution
            wait_seconds = self.calculate_wait_seconds()
            if wait_seconds > 0:
                logger.info(f"Waiting for start time {self.start_hour}:{self.start_minute:02d} "
                           f"({wait_seconds} seconds)...")
                time.sleep(wait_seconds)

            # Process files at the scheduled time
            if self.should_run_now():
                self.process_files()

            # After processing, the loop will continue and wait for the next day
