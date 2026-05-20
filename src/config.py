import os
from dataclasses import dataclass, field

from .exceptions import ConfigError

INPUT_DIR = "/app/input"
CACHE_DB = "/app/cache/converted-files.db"


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value is not None and value != "" else default


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as e:
        raise ConfigError(f"Invalid integer for {name}={value!r}: {e}")


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError as e:
        raise ConfigError(f"Invalid float for {name}={value!r}: {e}")


@dataclass
class AppConfig:
    debug_mode: bool = False


@dataclass
class ScheduleConfig:
    start_time: str = "04:00"
    run_immediately: bool = False


@dataclass
class FFMpegConfig:
    bitrate_stereo: str = "384k"
    bitrate_surround: str = "1536k"
    bitrate_surround_plus: str = "1664k"
    dialnorm: int = -27
    mixing_level: int = 80
    strict_mode: str = "-2"
    flags: str = "+genpts"
    timeout_seconds: int = 3600
    min_disk_space_ratio: float = 1.5
    threads: int = 0
    bufsize: str = "128k"
    performance_flags: str = "+discardcorrupt+genpts+igndts+ignidx"
    avoid_negative_ts: str = "make_zero"
    max_muxing_queue_size: int = 1024


@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    ffmpeg: FFMpegConfig = field(default_factory=FFMpegConfig)
    tz: str = "Europe/Paris"

    def get_parsed_start_time(self) -> tuple[int, int]:
        try:
            hour, minute = map(int, self.schedule.start_time.split(":"))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError("hour/minute out of range")
            return hour, minute
        except ValueError as e:
            raise ConfigError(f"Invalid START_TIME format '{self.schedule.start_time}': {e}")


def load_config() -> Config:
    """Build a Config from environment variables. Raises ConfigError on bad input."""
    cfg = Config(
        app=AppConfig(
            debug_mode=_env_bool("DEBUG_MODE", False),
        ),
        schedule=ScheduleConfig(
            start_time=_env_str("START_TIME", "04:00"),
            run_immediately=_env_bool("RUN_IMMEDIATELY", False),
        ),
        ffmpeg=FFMpegConfig(
            bitrate_stereo=_env_str("FFMPEG_BITRATE_STEREO", "384k"),
            bitrate_surround=_env_str("FFMPEG_BITRATE_SURROUND", "1536k"),
            bitrate_surround_plus=_env_str("FFMPEG_BITRATE_SURROUND_PLUS", "1664k"),
            dialnorm=_env_int("FFMPEG_DIALNORM", -27),
            mixing_level=_env_int("FFMPEG_MIXING_LEVEL", 80),
            strict_mode=_env_str("FFMPEG_STRICT_MODE", "-2"),
            flags=_env_str("FFMPEG_FLAGS", "+genpts"),
            timeout_seconds=_env_int("FFMPEG_TIMEOUT_SECONDS", 3600),
            min_disk_space_ratio=_env_float("FFMPEG_MIN_DISK_SPACE_RATIO", 1.5),
            threads=_env_int("FFMPEG_THREADS", 0),
            bufsize=_env_str("FFMPEG_BUFSIZE", "128k"),
            performance_flags=_env_str("FFMPEG_PERFORMANCE_FLAGS", "+discardcorrupt+genpts+igndts+ignidx"),
            avoid_negative_ts=_env_str("FFMPEG_AVOID_NEGATIVE_TS", "make_zero"),
            max_muxing_queue_size=_env_int("FFMPEG_MAX_MUXING_QUEUE_SIZE", 1024),
        ),
        tz=_env_str("TZ", "Europe/Paris"),
    )
    cfg.get_parsed_start_time()
    return cfg


def _initial_config() -> Config:
    """Eagerly load config at module import.

    Defaults are always valid, so this only fails when the user passes a
    malformed env var. We let the ConfigError propagate so main() can handle
    it cleanly instead of calling sys.exit() at module-load time.
    """
    return load_config()


config: Config = _initial_config()
