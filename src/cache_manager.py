import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("eac3_converter")


SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_files (
    file_key TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    size INTEGER,
    mtime REAL,
    action TEXT,
    timestamp TEXT,
    metadata_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_path ON processed_files(path);
"""


class CacheManager:
    """SQLite-backed cache of processed files."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), isolation_level=None)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.executescript(SCHEMA)
        logger.info(f"Cache DB opened at {self.db_path} ({self.get_cache_size()} entries)")

    def is_processed(self, file_key: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM processed_files WHERE file_key = ? LIMIT 1",
            (file_key,),
        ).fetchone()
        return row is not None

    def mark_processed(self, file_key: str, metadata: Dict[str, Any]) -> None:
        path = metadata.get("path", "")
        size = metadata.get("size")
        mtime = metadata.get("mtime")
        action = metadata.get("action")
        timestamp = metadata.get("timestamp")
        extras = {
            k: v for k, v in metadata.items()
            if k not in ("path", "size", "mtime", "action", "timestamp")
        }
        self.conn.execute(
            "INSERT OR REPLACE INTO processed_files "
            "(file_key, path, size, mtime, action, timestamp, metadata_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (file_key, path, size, mtime, action, timestamp, json.dumps(extras)),
        )

    def get_cache_size(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM processed_files").fetchone()
        return int(row[0]) if row else 0

    def close(self) -> None:
        try:
            self.conn.close()
            logger.debug("Cache DB connection closed")
        except Exception as e:
            logger.warning(f"Error closing cache DB: {e}")
