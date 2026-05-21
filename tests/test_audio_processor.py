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


@pytest.mark.parametrize("existing,channels,expected", [
    ("Français (DTS-HD MA 6.1)", 7, "Français (EAC3 6.1)"),
    ("Anglais (TRUEHD 7.1)", 8, "Anglais (EAC3 7.1)"),
    ("English [TrueHD 5.1]", 6, "English [EAC3 5.1]"),
    ("VF DTS 5.1", 6, "VF EAC3 5.1"),
    ("DTS-HD MA", 6, "EAC3"),
    ("", 8, "EAC3 7.1"),
    ("", 6, "EAC3 5.1"),
    ("", 2, "EAC3 Stereo"),
    ("Director Commentary", 2, "Director Commentary [EAC3]"),
])
def test_rewrite_title(existing, channels, expected):
    ap = AudioProcessor()
    assert ap._rewrite_title(existing, channels) == expected
