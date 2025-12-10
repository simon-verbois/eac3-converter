import sys
import tomli
from typing import Dict, Any

# Constants for fixed paths
INPUT_DIR = "/app/input"
CACHE_FILE = "/app/cache/converted-files.cache"


class Config:
    """Configuration manager for the EAC3 Converter."""

    def __init__(self, config_path: str = "/app/config/config.toml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from TOML file."""
        try:
            with open(self.config_path, "rb") as f:
                self._config = tomli.load(f)
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            sys.exit(1)

    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting."""
        return self._config.get("app", {}).get("debug_mode", False)

    @property
    def start_time(self) -> str:
        """Get start time in HH:MM format."""
        return self._config.get("schedule", {}).get("start_time", "04:00")

    @property
    def run_immediately(self) -> bool:
        """Get run immediately flag."""
        return self._config.get("schedule", {}).get("run_immediately", False)

    @property
    def timezone(self) -> str:
        """Get timezone setting."""
        return self._config.get("system", {}).get("timezone", "Europe/Paris")

    @property
    def ffmpeg_audio_bitrate(self) -> str:
        """Get ffmpeg audio bitrate setting."""
        return self._config.get("ffmpeg", {}).get("audio_bitrate", "640k")

    @property
    def ffmpeg_strict_mode(self) -> str:
        """Get ffmpeg strict mode setting."""
        return self._config.get("ffmpeg", {}).get("strict_mode", "-2")

    @property
    def ffmpeg_flags(self) -> str:
        """Get ffmpeg flags setting."""
        return self._config.get("ffmpeg", {}).get("flags", "+genpts")

    @property
    def ffmpeg_timeout_seconds(self) -> int:
        """Get ffmpeg timeout in seconds."""
        return self._config.get("ffmpeg", {}).get("timeout_seconds", 3600)

    @property
    def ffmpeg_min_disk_space_ratio(self) -> float:
        """Get minimum disk space ratio required."""
        return self._config.get("ffmpeg", {}).get("min_disk_space_ratio", 1.5)

    @property
    def ffmpeg_threads(self) -> int:
        """Get ffmpeg threads setting."""
        return self._config.get("ffmpeg", {}).get("threads", 0)

    @property
    def ffmpeg_bufsize(self) -> str:
        """Get ffmpeg buffer size setting."""
        return self._config.get("ffmpeg", {}).get("bufsize", "128k")

    @property
    def ffmpeg_performance_flags(self) -> str:
        """Get ffmpeg performance flags setting."""
        return self._config.get("ffmpeg", {}).get("performance_flags", "+discardcorrupt+genpts+igndts+ignidx")

    @property
    def ffmpeg_avoid_negative_ts(self) -> str:
        """Get ffmpeg avoid negative timestamps setting."""
        return self._config.get("ffmpeg", {}).get("avoid_negative_ts", "make_zero")

    @property
    def ffmpeg_max_muxing_queue_size(self) -> int:
        """Get ffmpeg max muxing queue size setting."""
        return self._config.get("ffmpeg", {}).get("max_muxing_queue_size", 1024)

    def get_parsed_start_time(self) -> tuple[int, int]:
        """Parse start time into hour and minute."""
        hour, minute = map(int, self.start_time.split(":"))
        return hour, minute


# Global config instance
config = Config()
