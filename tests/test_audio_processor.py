import pytest

from src.audio_processor import AudioProcessor
from src import config as config_module


@pytest.fixture(autouse=True)
def fresh_config(monkeypatch):
    """Ensure each test sees the default ffmpeg config.

    We mutate attributes on the existing singleton instead of replacing it,
    because audio_processor.py imported the `config` name by value.
    """
    ffmpeg = config_module.config.ffmpeg
    monkeypatch.setattr(ffmpeg, "bitrate_stereo", "384k")
    monkeypatch.setattr(ffmpeg, "bitrate_surround", "1536k")
    monkeypatch.setattr(ffmpeg, "bitrate_surround_plus", "1664k")
    monkeypatch.setattr(ffmpeg, "dialnorm", -27)
    monkeypatch.setattr(ffmpeg, "mixing_level", 80)


@pytest.mark.parametrize("channels,expected", [
    (1, "384k"),
    (2, "384k"),
    (3, "1536k"),
    (5, "1536k"),
    (6, "1536k"),
    (7, "1664k"),
    (8, "1664k"),
])
def test_bitrate_for_channels_defaults(channels, expected):
    ap = AudioProcessor()
    assert ap._bitrate_for_channels(channels) == expected


def test_bitrate_for_channels_respects_env(monkeypatch):
    monkeypatch.setattr(config_module.config.ffmpeg, "bitrate_surround", "1024k")
    ap = AudioProcessor()
    assert ap._bitrate_for_channels(6) == "1024k"
