import logging
import os
import time
from datetime import datetime, date

from .config import config
from .file_processor import FileProcessor

logger = logging.getLogger("eac3_converter")


class Scheduler:
    """Handles the scheduling and main processing loop."""

    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
        self.start_hour, self.start_minute = config.get_parsed_start_time()
        self.run_immediately = config.run_immediately
        self.input_dir = config.input_dir
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

        for file_path in files_to_process:
            self.file_processor.process_file(file_path)

        if not self.run_immediately:
            logger.info("Finishing daily processing...")

    def run(self) -> None:
        """Main processing loop."""
        logger.info("Starting watch service...")
        logger.debug(f"Configuration: INPUT_DIR={self.input_dir}, "
                    f"START_TIME={self.start_hour}:{self.start_minute:02d}, "
                    f"RUN_IMMEDIATELY={self.run_immediately}")

        while True:
            if self.should_run_now():
                self.process_files()

            time.sleep(60)  # Check every minute
