import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

from .config import config

logger = logging.getLogger("eac3_converter")


class AudioProcessor:
    """Handles audio stream detection and conversion."""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode

    def has_dts_or_truehd(self, file_path: str) -> bool:
        """Check if the file contains DTS or TrueHD audio tracks using ffprobe."""
        command = [
            "ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a",
            "-loglevel", "error", "-print_format", "json"
        ]

        logger.debug(f"Running ffprobe command: {' '.join(command)}")

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Failed to analyze audio tracks for {file_path}")
            return False

        try:
            streams = json.loads(result.stdout).get("streams", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to decode ffprobe output for {file_path}: {result.stdout}")
            return False

        logger.debug(f"Found {len(streams)} audio streams in {file_path}")
        for i, stream in enumerate(streams):
            codec_name = stream.get("codec_name", "").lower()
            logger.debug(f"Stream {i}: codec_name={codec_name}")
            if codec_name in ["dts", "truehd"]:
                return True
        return False

    def check_disk_space(self, file_path: str) -> bool:
        """Check if there's enough disk space for conversion (1.5x file size)."""
        try:
            file_size = os.path.getsize(file_path)
            required_space = int(file_size * config.ffmpeg_min_disk_space_ratio)

            # Get disk usage for the directory containing the file
            dir_path = os.path.dirname(os.path.abspath(file_path))
            stat = os.statvfs(dir_path)
            available_space = stat.f_bavail * stat.f_frsize

            logger.debug(f"File size: {file_size}, Required space: {required_space}, "
                        f"Available space: {available_space}")

            if available_space < required_space:
                logger.error(f"Insufficient disk space for {file_path}. "
                           f"Required: {required_space}, Available: {available_space}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking disk space for {file_path}: {e}")
            return False

    def convert_audio_tracks(self, input_file: str, temp_file: str) -> Dict[str, Any]:
        """Convert DTS or TrueHD tracks to EAC3 with performance optimizations."""
        start_time = time.time()

        command = [
            "ffmpeg", "-i", input_file, "-hide_banner",
            "-loglevel", "error" if not self.debug_mode else "info",
            "-threads", str(config.ffmpeg_threads),
            "-fflags", config.ffmpeg_performance_flags,
            "-avoid_negative_ts", config.ffmpeg_avoid_negative_ts,
            "-max_muxing_queue_size", str(config.ffmpeg_max_muxing_queue_size),
            "-b:a", config.ffmpeg_audio_bitrate, "-bufsize", config.ffmpeg_bufsize,
            "-strict", config.ffmpeg_strict_mode,
            "-map", "0", "-c:v", "copy", "-c:a", "eac3", "-c:s", "copy",
            temp_file, "-y"
        ]

        logger.debug(f"Running optimized ffmpeg command: {' '.join(command)}")
        logger.info("Starting ffmpeg conversion...")

        subprocess.run(command, check=True, timeout=config.ffmpeg_timeout_seconds)

        conversion_time = time.time() - start_time
        logger.info(f"Conversion completed in {conversion_time:.2f}s")

        return {
            "conversion_time": conversion_time,
            "command": " ".join(command)
        }

    def get_audio_streams_info(self, file_path: str) -> List[Dict[str, Any]]:
        """Get detailed information about audio streams."""
        command = [
            "ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a",
            "-loglevel", "error", "-print_format", "json"
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Failed to get audio streams info for {file_path}")
            return []

        try:
            data = json.loads(result.stdout)
            return data.get("streams", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse audio streams info for {file_path}")
            return []
