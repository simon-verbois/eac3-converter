import pytest

from src.config import load_config
from src.exceptions import ConfigError

ENV_VARS = [
    "DEBUG_MODE", "START_TIME", "RUN_IMMEDIATELY", "TZ",
    "FFMPEG_AUDIO_BITRATE", "FFMPEG_STRICT_MODE", "FFMPEG_FLAGS",
    "FFMPEG_TIMEOUT_SECONDS", "FFMPEG_MIN_DISK_SPACE_RATIO", "FFMPEG_THREADS",
    "FFMPEG_BUFSIZE", "FFMPEG_PERFORMANCE_FLAGS", "FFMPEG_AVOID_NEGATIVE_TS",
    "FFMPEG_MAX_MUXING_QUEUE_SIZE",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_defaults_apply_when_no_env_set():
    cfg = load_config()
    assert cfg.app.debug_mode is False
    assert cfg.schedule.start_time == "04:00"
    assert cfg.schedule.run_immediately is False
    assert cfg.tz == "Europe/Paris"
    assert cfg.ffmpeg.audio_bitrate == "640k"
    assert cfg.ffmpeg.timeout_seconds == 3600
    assert cfg.ffmpeg.min_disk_space_ratio == 1.5
    assert cfg.ffmpeg.threads == 0


@pytest.mark.parametrize("value", ["true", "True", "1", "yes", "ON"])
def test_debug_mode_truthy(monkeypatch, value):
    monkeypatch.setenv("DEBUG_MODE", value)
    assert load_config().app.debug_mode is True


@pytest.mark.parametrize("value", ["false", "0", "no", "", "anything-else"])
def test_debug_mode_falsy(monkeypatch, value):
    monkeypatch.setenv("DEBUG_MODE", value)
    assert load_config().app.debug_mode is False


def test_int_env_parsed(monkeypatch):
    monkeypatch.setenv("FFMPEG_TIMEOUT_SECONDS", "7200")
    monkeypatch.setenv("FFMPEG_THREADS", "8")
    cfg = load_config()
    assert cfg.ffmpeg.timeout_seconds == 7200
    assert cfg.ffmpeg.threads == 8


def test_float_env_parsed(monkeypatch):
    monkeypatch.setenv("FFMPEG_MIN_DISK_SPACE_RATIO", "2.0")
    assert load_config().ffmpeg.min_disk_space_ratio == 2.0


def test_invalid_int_raises(monkeypatch):
    monkeypatch.setenv("FFMPEG_TIMEOUT_SECONDS", "not-a-number")
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_start_time_raises(monkeypatch):
    monkeypatch.setenv("START_TIME", "not-a-time")
    with pytest.raises(ConfigError):
        load_config()


def test_out_of_range_start_time_raises(monkeypatch):
    monkeypatch.setenv("START_TIME", "25:00")
    with pytest.raises(ConfigError):
        load_config()


def test_get_parsed_start_time(monkeypatch):
    monkeypatch.setenv("START_TIME", "21:30")
    cfg = load_config()
    assert cfg.get_parsed_start_time() == (21, 30)
