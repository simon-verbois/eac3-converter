from src.cache_manager import CacheManager


def make_cm(tmp_path):
    return CacheManager(str(tmp_path / "cache.db"))


def test_creates_db_file(tmp_path):
    db = tmp_path / "cache.db"
    cm = make_cm(tmp_path)
    assert db.exists()
    cm.close()


def test_is_processed_false_for_unknown_key(tmp_path):
    cm = make_cm(tmp_path)
    assert cm.is_processed("unknown") is False
    cm.close()


def test_mark_then_is_processed(tmp_path):
    cm = make_cm(tmp_path)
    cm.mark_processed("key1", {"action": "converted", "timestamp": "2026-05-20"})
    assert cm.is_processed("key1") is True
    cm.close()


def test_get_cache_size(tmp_path):
    cm = make_cm(tmp_path)
    assert cm.get_cache_size() == 0
    cm.mark_processed("a", {"action": "skipped"})
    cm.mark_processed("b", {"action": "converted"})
    cm.mark_processed("c", {"action": "failed"})
    assert cm.get_cache_size() == 3
    cm.close()


def test_insert_or_replace_does_not_duplicate(tmp_path):
    cm = make_cm(tmp_path)
    cm.mark_processed("k", {"action": "converted", "timestamp": "t1"})
    cm.mark_processed("k", {"action": "failed", "timestamp": "t2"})
    assert cm.get_cache_size() == 1
    cm.close()


def test_persistence_across_instances(tmp_path):
    cm1 = make_cm(tmp_path)
    cm1.mark_processed("persisted", {"action": "converted"})
    cm1.close()

    cm2 = make_cm(tmp_path)
    assert cm2.is_processed("persisted") is True
    assert cm2.get_cache_size() == 1
    cm2.close()


def test_metadata_extras_stored_as_json(tmp_path):
    import json
    cm = make_cm(tmp_path)
    cm.mark_processed("k", {
        "action": "converted",
        "conversion_time": 12.5,
        "ffmpeg_command": "ffmpeg -i ...",
    })
    row = cm.conn.execute(
        "SELECT metadata_json FROM processed_files WHERE file_key=?", ("k",)
    ).fetchone()
    extras = json.loads(row[0])
    assert extras["conversion_time"] == 12.5
    assert "ffmpeg_command" in extras
    cm.close()
