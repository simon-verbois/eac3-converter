import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("eac3_converter")


class CacheManager:
    """Manages the cache of processed files."""

    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, Any] = {}
        self._ensure_cache_directory()

    def _ensure_cache_directory(self):
        """Ensure the cache directory exists."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def load_cache(self) -> Dict[str, Any]:
        """Load the cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded cache with {len(self.cache)} entries")
            except json.JSONDecodeError:
                logger.warning(f"Cache file {self.cache_file} is corrupted. Creating new cache.")
                self.cache = {}
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self.cache = {}
        else:
            logger.info("No existing cache file found, starting with empty cache")
            self.cache = {}
        return self.cache

    def save_cache(self):
        """Save the cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Saved cache with {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def is_processed(self, file_key: str) -> bool:
        """Check if a file has been processed."""
        return file_key in self.cache

    def mark_processed(self, file_key: str, metadata: Dict[str, Any]):
        """Mark a file as processed with metadata."""
        self.cache[file_key] = metadata
        self.save_cache()

    def get_cache_size(self) -> int:
        """Get the number of cached entries."""
        return len(self.cache)
