import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any

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

    def convert_audio_tracks(self, input_file: str, temp_file: str) -> None:
        """Convert DTS or TrueHD tracks to EAC3."""
        command = [
            "ffmpeg", "-i", input_file, "-hide_banner",
            "-loglevel", "error" if not self.debug_mode else "info",
            "-b:a", "640k", "-strict", "-2",
            "-fflags", "+genpts", "-map", "0", "-c:v", "copy", "-c:a", "eac3",
            "-c:s", "copy", temp_file, "-y"
        ]

        logger.debug(f"Running ffmpeg command: {' '.join(command)}")

        subprocess.run(command, check=True)
        logger.info("Audio conversion completed")

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
