from unittest.mock import MagicMock

import pytest

from src import config as config_module
from src.cache_manager import CacheManager
from src.file_processor import FileProcessor


@pytest.fixture(autouse=True)
def standalone_defaults(monkeypatch):
    sa = config_module.config.standalone_audio
    monkeypatch.setattr(sa, "enabled", True)
    monkeypatch.setattr(sa, "extensions", ("dts", "thd", "truehd", "dtshd"))
    monkeypatch.setattr(sa, "keep_original", False)
    monkeypatch.setattr(sa, "output_extension", "ec3")


def make_processor(tmp_path):
    cache = CacheManager(str(tmp_path / "cache.db"))
    audio = MagicMock()
    return FileProcessor(cache, audio), cache, audio


def test_find_standalone_audio_files_matches_configured_extensions(tmp_path, monkeypatch):
    (tmp_path / "movie.mkv").write_bytes(b"x")
    (tmp_path / "track.dts").write_bytes(b"x")
    (tmp_path / "other.thd").write_bytes(b"x")
    (tmp_path / "skip.flac").write_bytes(b"x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.truehd").write_bytes(b"x")
    (sub / ".temp_ignored.dts").write_bytes(b"x")

    fp, cache, _ = make_processor(tmp_path)
    found = sorted(fp.find_standalone_audio_files(str(tmp_path)))
    cache.close()

    assert found == sorted([
        str(tmp_path / "track.dts"),
        str(tmp_path / "other.thd"),
        str(sub / "nested.truehd"),
    ])


def test_find_standalone_audio_files_empty_extensions(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module.config.standalone_audio, "extensions", ())
    (tmp_path / "track.dts").write_bytes(b"x")
    fp, cache, _ = make_processor(tmp_path)
    assert fp.find_standalone_audio_files(str(tmp_path)) == []
    cache.close()


def test_process_standalone_skips_when_already_eac3(tmp_path):
    src = tmp_path / "track.dts"
    src.write_bytes(b"x")

    fp, cache, audio = make_processor(tmp_path)
    audio.get_audio_streams_info.return_value = [{"codec_name": "eac3", "channels": 6}]

    fp.process_standalone_audio_file(str(src))

    audio.convert_standalone_audio.assert_not_called()
    assert src.exists()
    cache.close()


def test_process_standalone_skips_unsupported_codec(tmp_path):
    src = tmp_path / "track.dts"
    src.write_bytes(b"x")

    fp, cache, audio = make_processor(tmp_path)
    audio.get_audio_streams_info.return_value = [{"codec_name": "flac", "channels": 2}]

    fp.process_standalone_audio_file(str(src))

    audio.convert_standalone_audio.assert_not_called()
    assert src.exists()
    cache.close()


def test_process_standalone_converts_dts_and_removes_original(tmp_path):
    src = tmp_path / "track.dts"
    src.write_bytes(b"x")

    fp, cache, audio = make_processor(tmp_path)
    audio.get_audio_streams_info.return_value = [{"codec_name": "dts", "channels": 6}]
    audio.check_disk_space.return_value = True

    def fake_convert(input_file, temp_file):
        # Simulate ffmpeg producing the temp output.
        from pathlib import Path
        Path(temp_file).write_bytes(b"converted")
        return {"conversion_time": 1.23, "command": "ffmpeg ..."}

    audio.convert_standalone_audio.side_effect = fake_convert

    fp.process_standalone_audio_file(str(src))

    audio.convert_standalone_audio.assert_called_once()
    assert not src.exists(), "original .dts should be removed when keep_original=False"
    assert (tmp_path / "track.ec3").exists()
    cache.close()


def test_process_standalone_keeps_original_when_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module.config.standalone_audio, "keep_original", True)
    src = tmp_path / "track.dts"
    src.write_bytes(b"x")

    fp, cache, audio = make_processor(tmp_path)
    audio.get_audio_streams_info.return_value = [{"codec_name": "dts", "channels": 6}]
    audio.check_disk_space.return_value = True

    def fake_convert(input_file, temp_file):
        from pathlib import Path
        Path(temp_file).write_bytes(b"converted")
        return {"conversion_time": 1.23, "command": "ffmpeg ..."}

    audio.convert_standalone_audio.side_effect = fake_convert

    fp.process_standalone_audio_file(str(src))

    assert src.exists(), "original .dts should be kept when keep_original=True"
    assert (tmp_path / "track.ec3").exists()
    cache.close()


def test_process_standalone_cache_hit_short_circuits(tmp_path):
    src = tmp_path / "track.dts"
    src.write_bytes(b"x")

    fp, cache, audio = make_processor(tmp_path)
    audio.get_audio_streams_info.return_value = [{"codec_name": "dts", "channels": 6}]
    audio.check_disk_space.return_value = True

    def fake_convert(input_file, temp_file):
        from pathlib import Path
        Path(temp_file).write_bytes(b"converted")
        return {"conversion_time": 1.0, "command": "ffmpeg ..."}

    audio.convert_standalone_audio.side_effect = fake_convert

    # First run converts.
    fp.process_standalone_audio_file(str(src))
    assert audio.convert_standalone_audio.call_count == 1

    # Recreate the .dts to test the cache short-circuit on identical metadata.
    # Cache key includes size+mtime; since we removed the file, simulate a kept-original scenario:
    src.write_bytes(b"x")
    # Reset mock and re-run; new file => different mtime => not cached.
    # Instead, verify the cache hit path by re-processing the same path with same stat.
    # Force the path back into the cache directly.
    metadata = fp.get_file_metadata(str(src))
    key = fp.generate_file_key(str(src), metadata)
    cache.mark_processed(key, {"action": "converted"})
    audio.convert_standalone_audio.reset_mock()

    fp.process_standalone_audio_file(str(src))
    audio.convert_standalone_audio.assert_not_called()
    cache.close()
