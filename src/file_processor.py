import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .audio_processor import AudioProcessor
from .cache_manager import CacheManager
from .exceptions import ConversionError, ConversionTimeoutError, DiskSpaceError, FileProcessingError

logger = logging.getLogger("eac3_converter")


class FileProcessor:
    """Handles file metadata extraction and processing."""

    def __init__(self, cache_manager: CacheManager, audio_processor: AudioProcessor):
        self.cache_manager = cache_manager
        self.audio_processor = audio_processor

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata for cache identification."""
        try:
            stat_info = os.stat(file_path)
            metadata = {
                "path": file_path,
                "size": stat_info.st_size,
                "mtime": stat_info.st_mtime,
                "ctime": stat_info.st_ctime
            }
            logger.debug(f"File metadata for {file_path}: size={metadata['size']}, mtime={metadata['mtime']}")
            return metadata
        except FileNotFoundError:
            logger.error(f"File disappeared during processing: {file_path}")
            return None

    def generate_file_key(self, file_path: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique key for file caching."""
        return f"{file_path}_{metadata['size']}_{metadata['mtime']}"

    def process_file(self, file_path: str) -> None:
        """Process a single file, using cache to avoid re-processing."""
        filename = Path(file_path).name
        file_metadata = self.get_file_metadata(file_path)

        if file_metadata is None:
            return

        file_key = self.generate_file_key(file_path, file_metadata)

        logger.debug(f"Processing file: {filename} with key: {file_key}")

        if self.cache_manager.is_processed(file_key):
            logger.debug(f"Cache hit for {filename} with key: {file_key}")
            logger.info(f"Skipping {filename} (already processed according to cache)")
            return

        logger.debug(f"Cache miss for {filename} with key: {file_key}")

        temp_file = Path(file_path).parent / f".temp_{filename}"

        if self.audio_processor.has_dts_or_truehd(file_path):
            try:
                # Check disk space before starting conversion - now raises DiskSpaceError
                self.audio_processor.check_disk_space(file_path)

                logger.info(f"Converting audio tracks for {filename}...")
                conversion_metrics = self.audio_processor.convert_audio_tracks(file_path, str(temp_file))
                logger.info(f"Conversion completed for {filename}.")

                # Check if temp file exists before replacement
                if not temp_file.exists():
                    raise FileProcessingError(f"Temporary file {temp_file} does not exist after conversion")

                os.replace(temp_file, file_path)
                logger.info(f"File {filename} replaced successfully.")

                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "converted",
                    "original_codecs": "dts_or_truehd",
                    "conversion_time": conversion_metrics["conversion_time"],
                    "ffmpeg_command": conversion_metrics["command"]
                }
                self.cache_manager.mark_processed(file_key, metadata)
                logger.info(f"Metrics: conversion_time={conversion_metrics['conversion_time']:.2f}s")

            except DiskSpaceError as e:
                logger.error(f"Skipping conversion of {filename}: {e}")
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "skipped",
                    "reason": "insufficient_disk_space",
                    "error": str(e)
                }
                self.cache_manager.mark_processed(file_key, metadata)
                return

            except (ConversionError, ConversionTimeoutError) as e:
                logger.error(f"Conversion failed for {filename}: {e}")
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "failed",
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
                self.cache_manager.mark_processed(file_key, metadata)
                # Clean up the temporary file if conversion fails
                if temp_file.exists():
                    temp_file.unlink()
                return

            except Exception as e:
                logger.error(f"Unexpected error processing {filename}: {e}")
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "failed",
                    "error_type": "unexpected_error",
                    "error": str(e)
                }
                self.cache_manager.mark_processed(file_key, metadata)
                # Clean up the temporary file if conversion fails
                if temp_file.exists():
                    temp_file.unlink()
                return
        else:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "action": "skipped",
                "reason": "no_dts_or_truehd"
            }
            self.cache_manager.mark_processed(file_key, metadata)
            logger.info(f"No DTS or TrueHD tracks found in {filename}, skipping.")

    def find_mkv_files(self, input_dir: str) -> list[str]:
        """Find all MKV files in the input directory recursively, excluding temporary files."""
        mkv_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".mkv") and not file.startswith(".temp_"):
                    mkv_files.append(os.path.join(root, file))
        logger.debug(f"Found {len(mkv_files)} MKV files in {input_dir}")
        return mkv_files
