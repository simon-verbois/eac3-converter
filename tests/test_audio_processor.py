import pytest

from src.audio_processor import AudioProcessor, resolve_audio_profile
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


# --- resolve_audio_profile ------------------------------------------------

@pytest.mark.parametrize("channels,expected", [
    (1, {"bitrate": "128k", "channels": 1, "title": "EAC3 Mono"}),
    (2, {"bitrate": "192k", "channels": 2, "title": "EAC3 Stereo"}),
    (6, {"bitrate": "640k", "channels": 6, "title": "EAC3 5.1"}),
    (8, {"bitrate": "640k", "channels": 6, "title": "EAC3 5.1"}),
])
def test_resolve_eac3_audio_profile(channels, expected):
    assert resolve_audio_profile("eac3", channels) == expected


def test_resolve_ac3_audio_profile():
    assert resolve_audio_profile("ac3", 1) == {
        "bitrate": "128k", "channels": 1, "title": "AC3 Mono"
    }
    assert resolve_audio_profile("ac3", 2) == {
        "bitrate": "192k", "channels": 2, "title": "AC3 Stereo"
    }
    assert resolve_audio_profile("ac3", 6) == {
        "bitrate": "640k", "channels": 6, "title": "AC3 5.1"
    }
    assert resolve_audio_profile("ac3", 8) == {
        "bitrate": "640k", "channels": 6, "title": "AC3 5.1"
    }


def test_resolve_audio_profile_rejects_unknown_codec():
    with pytest.raises(ValueError):
        resolve_audio_profile("aac", 2)


def test_eac3_profile_ignores_deprecated_kbps_per_channel(monkeypatch):
    monkeypatch.setattr(config_module.config.ffmpeg, "kbps_per_channel", 1000)
    assert resolve_audio_profile("eac3", 6) == {
        "bitrate": "640k", "channels": 6, "title": "EAC3 5.1"
    }


# --- convert_audio_tracks -------------------------------------------------

def test_convert_audio_tracks_uses_fixed_eac3_profiles(monkeypatch):
    ap = AudioProcessor()
    ap.get_audio_streams_info = lambda _: [
        {
            "codec_name": "truehd",
            "channels": 8,
            "tags": {"title": "TrueHD Atmos 7.1"},
        },
        {
            "codec_name": "dts",
            "profile": "DTS-HD MA",
            "channels": 6,
            "tags": {"title": "DTS-HD MA 5.1"},
        },
        {
            "codec_name": "ac3",
            "channels": 6,
            "tags": {"title": "AC3 5.1"},
        },
    ]

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command

    monkeypatch.setattr("src.audio_processor.subprocess.run", fake_run)

    ap.convert_audio_tracks("input.mkv", "output.mkv")

    command = captured["command"]
    assert command[command.index("-c:a:0") + 1] == "eac3"
    assert command[command.index("-b:a:0") + 1] == "640k"
    assert command[command.index("-ac:a:0") + 1] == "6"
    assert command[command.index("-metadata:s:a:0") + 1] == "title=EAC3 5.1"

    assert command[command.index("-c:a:1") + 1] == "eac3"
    assert command[command.index("-b:a:1") + 1] == "640k"
    assert command[command.index("-ac:a:1") + 1] == "6"
    assert command[command.index("-metadata:s:a:1") + 1] == "title=EAC3 5.1"

    assert command[command.index("-c:a:2") + 1] == "copy"
    assert "Atmos" not in " ".join(command)


def test_convert_audio_tracks_uses_stereo_profile(monkeypatch):
    ap = AudioProcessor()
    ap.get_audio_streams_info = lambda _: [
        {"codec_name": "dts", "channels": 2, "tags": {"title": "DTS Stereo"}},
    ]

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command

    monkeypatch.setattr("src.audio_processor.subprocess.run", fake_run)

    ap.convert_audio_tracks("input.mkv", "output.mkv")

    command = captured["command"]
    assert command[command.index("-b:a:0") + 1] == "192k"
    assert command[command.index("-ac:a:0") + 1] == "2"
    assert command[command.index("-metadata:s:a:0") + 1] == "title=EAC3 Stereo"


def test_convert_standalone_audio_uses_fixed_eac3_profile(monkeypatch):
    ap = AudioProcessor()
    ap.get_audio_streams_info = lambda _: [
        {"codec_name": "dts", "channels": 6, "profile": "DTS-HD MA"},
    ]

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command

    monkeypatch.setattr("src.audio_processor.subprocess.run", fake_run)

    ap.convert_standalone_audio("track.dts", "track.ec3")

    command = captured["command"]
    assert command[command.index("-b:a") + 1] == "640k"
    assert command[command.index("-ac:a") + 1] == "6"
