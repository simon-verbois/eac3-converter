import os
import sys
import tomli
from typing import Dict, Any


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
    def input_dir(self) -> str:
        """Get input directory path."""
        return self._config.get("paths", {}).get("input_dir", "/app/input")

    @property
    def cache_file(self) -> str:
        """Get cache file path."""
        return self._config.get("paths", {}).get("cache_file", "/app/cache/converted-files.cache")

    @property
    def timezone(self) -> str:
        """Get timezone setting."""
        return self._config.get("system", {}).get("timezone", "Europe/Paris")

    def get_parsed_start_time(self) -> tuple[int, int]:
        """Parse start time into hour and minute."""
        hour, minute = map(int, self.start_time.split(":"))
        return hour, minute


# Global config instance
config = Config()
