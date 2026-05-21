import pytest

from src.audio_processor import AudioProcessor
from src import config as config_module


@pytest.fixture(autouse=True)
def fresh_config(monkeypatch):
    """Reset ffmpeg config attributes to defaults for each test.

    audio_processor.py imported the `config` name by value, so we mutate
    the singleton's attributes instead of reassigning it.
    """
    ffmpeg = config_module.config.ffmpeg
    monkeypatch.setattr(ffmpeg, "kbps_per_channel", 256)
    monkeypatch.setattr(ffmpeg, "dialnorm", -27)
    monkeypatch.setattr(ffmpeg, "mixing_level", 80)


# --- _target_bitrate -------------------------------------------------------

@pytest.mark.parametrize("channels,expected", [
    (1, "256k"),    # mono
    (2, "512k"),    # stereo
    (6, "1536k"),   # 5.1
    (7, "1792k"),   # 6.1
    (8, "2048k"),   # 7.1
])
def test_target_bitrate_lossless_default(channels, expected):
    """TrueHD (lossless): always use channels * kbps_per_channel."""
    ap = AudioProcessor()
    stream = {"channels": channels, "codec_name": "truehd"}
    assert ap._target_bitrate(stream) == expected


def test_target_bitrate_dts_hd_ma_treated_as_lossless():
    ap = AudioProcessor()
    stream = {
        "channels": 6,
        "codec_name": "dts",
        "profile": "DTS-HD MA",
        "bit_rate": "3000000",  # ignored because lossless
    }
    assert ap._target_bitrate(stream) == "1536k"


def test_target_bitrate_dts_lossy_capped_at_source():
    """DTS core at 768k 5.1: don't encode higher than source."""
    ap = AudioProcessor()
    stream = {
        "channels": 6,
        "codec_name": "dts",
        "profile": "DTS",
        "bit_rate": "768000",
    }
    assert ap._target_bitrate(stream) == "768k"


def test_target_bitrate_dts_lossy_above_source_uses_full_target():
    """DTS core at 1509k 5.1: target 1536k > source, but cap to 1509k."""
    ap = AudioProcessor()
    stream = {
        "channels": 6,
        "codec_name": "dts",
        "profile": "DTS",
        "bit_rate": "1509000",
    }
    assert ap._target_bitrate(stream) == "1509k"


def test_target_bitrate_dts_hra_capped():
    """DTS-HD HRA is lossy → cap applies."""
    ap = AudioProcessor()
    stream = {
        "channels": 6,
        "codec_name": "dts",
        "profile": "DTS-HD HRA",
        "bit_rate": "1024000",
    }
    assert ap._target_bitrate(stream) == "1024k"


def test_target_bitrate_lossy_without_source_bitrate():
    """Lossy source but no bit_rate reported → fall back to full target."""
    ap = AudioProcessor()
    stream = {"channels": 6, "codec_name": "dts", "profile": "DTS"}
    assert ap._target_bitrate(stream) == "1536k"


def test_target_bitrate_clamped_to_ffmpeg_max(monkeypatch):
    monkeypatch.setattr(config_module.config.ffmpeg, "kbps_per_channel", 1000)
    ap = AudioProcessor()
    stream = {"channels": 8, "codec_name": "truehd"}
    # 8000k would be > 6144k cap
    assert ap._target_bitrate(stream) == "6144k"


def test_target_bitrate_respects_env(monkeypatch):
    monkeypatch.setattr(config_module.config.ffmpeg, "kbps_per_channel", 128)
    ap = AudioProcessor()
    stream = {"channels": 6, "codec_name": "truehd"}
    assert ap._target_bitrate(stream) == "768k"


# --- _is_lossless ----------------------------------------------------------

@pytest.mark.parametrize("codec,profile,expected", [
    ("truehd", "", True),
    ("truehd", None, True),
    ("dts", "DTS-HD MA", True),
    ("dts", "dts-hd ma", True),
    ("dts", "DTS", False),
    ("dts", "DTS-HD HRA", False),
    ("dts", "DTS-ES", False),
    ("dts", "", False),
    ("ac3", "", False),
])
def test_is_lossless(codec, profile, expected):
    assert AudioProcessor._is_lossless(codec, profile) is expected


# --- _rewrite_title --------------------------------------------------------

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
