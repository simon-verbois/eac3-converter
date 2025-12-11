import sys
import tomli
from dataclasses import dataclass
from typing import Dict, Any

from .exceptions import ConfigError

# Constants for fixed paths
INPUT_DIR = "/app/input"
CACHE_FILE = "/app/cache/converted-files.cache"


@dataclass
class AppConfig:
    """Application configuration."""
    debug_mode: bool = False


@dataclass
class ScheduleConfig:
    """Scheduling configuration."""
    start_time: str = "04:00"
    run_immediately: bool = False


@dataclass
class SystemConfig:
    """System configuration."""
    timezone: str = "Europe/Paris"


@dataclass
class FFMpegConfig:
    """FFmpeg configuration."""
    audio_bitrate: str = "640k"
    strict_mode: str = "-2"
    flags: str = "+genpts"
    timeout_seconds: int = 3600
    min_disk_space_ratio: float = 1.5
    threads: int = 0
    bufsize: str = "128k"
    performance_flags: str = "+discardcorrupt+genpts+igndts+ignidx"
    avoid_negative_ts: str = "make_zero"
    max_muxing_queue_size: int = 1024


class Config:
    """Configuration manager for the EAC3 Converter."""

    def __init__(self, config_path: str = "/app/config/config.toml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

        # Initialize config sections
        self.app = AppConfig(**self._config.get("app", {}))
        self.schedule = ScheduleConfig(**self._config.get("schedule", {}))
        self.system = SystemConfig(**self._config.get("system", {}))
        self.ffmpeg = FFMpegConfig(**self._config.get("ffmpeg", {}))

    def _load_config(self) -> None:
        """Load configuration from TOML file."""
        try:
            with open(self.config_path, "rb") as f:
                self._config = tomli.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found: {self.config_path}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")

    def get_parsed_start_time(self) -> tuple[int, int]:
        """Parse start time into hour and minute."""
        try:
            hour, minute = map(int, self.schedule.start_time.split(":"))
            return hour, minute
        except ValueError as e:
            raise ConfigError(f"Invalid start_time format '{self.schedule.start_time}': {e}")


# Global config instance
try:
    config = Config()
except ConfigError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
