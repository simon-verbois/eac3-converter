import json
import logging
import os
import subprocess
import time
from typing import List, Dict, Any

from .config import config
from .exceptions import ConversionError, ConversionTimeoutError, DiskSpaceError

logger = logging.getLogger("eac3_converter")

AUDIO_PROFILES = {
    "eac3": {
        1: {"bitrate": "128k", "channels": 1, "title": "EAC3 Mono"},
        2: {"bitrate": "192k", "channels": 2, "title": "EAC3 Stereo"},
        6: {"bitrate": "640k", "channels": 6, "title": "EAC3 5.1"},
        8: {"bitrate": "768k", "channels": 8, "title": "EAC3 7.1"},
    },
    "ac3": {
        1: {"bitrate": "128k", "channels": 1, "title": "AC3 Mono"},
        2: {"bitrate": "192k", "channels": 2, "title": "AC3 Stereo"},
        6: {"bitrate": "640k", "channels": 6, "title": "AC3 5.1"},
    },
}


def resolve_audio_profile(target_codec: str, source_channels: int) -> Dict[str, Any]:
    """Resolve a fixed Plex-safe audio output profile.

    EAC3 7.1 support varies across ffmpeg/Plex environments, so 7.1/8ch
    sources intentionally fall back to EAC3 5.1 by default.
    """
    codec = (target_codec or "").lower()
    if codec not in AUDIO_PROFILES:
        raise ValueError(f"Unsupported target audio codec: {target_codec}")

    try:
        channels = int(source_channels or 2)
    except (TypeError, ValueError):
        channels = 2

    if channels <= 1:
        profile_channels = 1
    elif channels == 2:
        profile_channels = 2
    else:
        profile_channels = 6

    profile = AUDIO_PROFILES[codec][profile_channels]
    return dict(profile)


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
            required_space = int(file_size * config.ffmpeg.min_disk_space_ratio)

            # Get disk usage for the directory containing the file
            dir_path = os.path.dirname(os.path.abspath(file_path))
            stat = os.statvfs(dir_path)
            available_space = stat.f_bavail * stat.f_frsize

            logger.debug(f"File size: {file_size}, Required space: {required_space}, "
                        f"Available space: {available_space}")

            if available_space < required_space:
                error_msg = (f"Insufficient disk space for {file_path}. "
                           f"Required: {required_space}, Available: {available_space}")
                logger.error(error_msg)
                raise DiskSpaceError(error_msg)

            return True
        except DiskSpaceError:
            raise  # Re-raise our custom exception
        except Exception as e:
            logger.error(f"Error checking disk space for {file_path}: {e}")
            return False

    def convert_audio_tracks(self, input_file: str, temp_file: str) -> Dict[str, Any]:
        """Re-encode DTS/TrueHD audio streams to EAC3; copy other streams as-is.

        Output bitrate, channels and title are chosen from fixed profiles.
        Streams that are neither DTS nor TrueHD are passed through with
        -c:a:N copy.
        """
        start_time = time.time()

        streams = self.get_audio_streams_info(input_file)
        per_stream_codec_args: List[str] = []
        encoded_count = 0
        copied_count = 0
        for i, stream in enumerate(streams):
            codec = (stream.get("codec_name") or "").lower()
            channels = int(stream.get("channels", 2) or 2)
            if codec in ("dts", "truehd"):
                profile = resolve_audio_profile("eac3", channels)
                existing_title = (stream.get("tags") or {}).get("title", "")
                per_stream_codec_args.extend([
                    f"-c:a:{i}", "eac3",
                    f"-b:a:{i}", profile["bitrate"],
                    f"-ac:a:{i}", str(profile["channels"]),
                    f"-metadata:s:a:{i}", f"title={profile['title']}",
                ])
                logger.info(
                    f"Stream {i}: {codec} {channels}ch -> eac3 "
                    f"{profile['channels']}ch @ {profile['bitrate']} "
                    f"(title: '{existing_title}' -> '{profile['title']}')"
                )
                encoded_count += 1
            else:
                per_stream_codec_args.extend([f"-c:a:{i}", "copy"])
                logger.info(
                    f"Stream {i}: {codec or 'unknown'} {channels}ch -> copy"
                )
                copied_count += 1

        logger.info(
            f"Audio plan: {encoded_count} stream(s) to EAC3, "
            f"{copied_count} stream(s) copied"
        )

        command = [
            "ffmpeg", "-i", input_file, "-hide_banner",
            "-loglevel", "error" if not self.debug_mode else "info",
            "-threads", str(config.ffmpeg.threads),
            "-fflags", config.ffmpeg.performance_flags,
            "-avoid_negative_ts", config.ffmpeg.avoid_negative_ts,
            "-max_muxing_queue_size", str(config.ffmpeg.max_muxing_queue_size),
            "-bufsize", config.ffmpeg.bufsize,
            "-strict", config.ffmpeg.strict_mode,
            "-map", "0", "-c:v", "copy", "-c:s", "copy",
            *per_stream_codec_args,
            "-dialnorm", str(config.ffmpeg.dialnorm),
            "-mixing_level", str(config.ffmpeg.mixing_level),
            temp_file, "-y"
        ]

        logger.debug(f"Running optimized ffmpeg command: {' '.join(command)}")
        logger.info("Starting ffmpeg conversion...")

        try:
            result = subprocess.run(command, check=True, timeout=config.ffmpeg.timeout_seconds,
                                  capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for {input_file} after {config.ffmpeg.timeout_seconds}s")
            raise ConversionTimeoutError(f"Timeout after {config.ffmpeg.timeout_seconds}s for {input_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed with return code {e.returncode}: {e.stderr}")
            raise ConversionError(f"ffmpeg error (code {e.returncode}): {e.stderr.strip()}")
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {e}")
            raise ConversionError(f"Unexpected conversion error: {e}")

        conversion_time = time.time() - start_time
        logger.info(f"Conversion completed in {conversion_time:.2f}s")

        return {
            "conversion_time": conversion_time,
            "command": " ".join(command)
        }

    def convert_standalone_audio(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """Convert a standalone audio file (e.g. .dts) to a standalone EAC3 file."""
        start_time = time.time()

        streams = self.get_audio_streams_info(input_file)
        channels = int(streams[0].get("channels", 2) or 2) if streams else 2
        profile = resolve_audio_profile("eac3", channels)
        logger.debug(
            f"Standalone audio: channels={channels} -> eac3 "
            f"{profile['channels']}ch @ {profile['bitrate']}"
        )

        command = [
            "ffmpeg", "-i", input_file, "-hide_banner",
            "-loglevel", "error" if not self.debug_mode else "info",
            "-threads", str(config.ffmpeg.threads),
            "-strict", config.ffmpeg.strict_mode,
            "-vn", "-map", "0:a", "-c:a", "eac3",
            "-b:a", profile["bitrate"],
            "-ac:a", str(profile["channels"]),
            "-dialnorm", str(config.ffmpeg.dialnorm),
            "-mixing_level", str(config.ffmpeg.mixing_level),
            "-f", "eac3",
            output_file, "-y"
        ]

        logger.debug(f"Running standalone ffmpeg command: {' '.join(command)}")
        logger.info("Starting standalone audio conversion...")

        try:
            subprocess.run(command, check=True, timeout=config.ffmpeg.timeout_seconds,
                           capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            logger.error(f"Standalone conversion timeout for {input_file} after {config.ffmpeg.timeout_seconds}s")
            raise ConversionTimeoutError(f"Timeout after {config.ffmpeg.timeout_seconds}s for {input_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed with return code {e.returncode}: {e.stderr}")
            raise ConversionError(f"ffmpeg error (code {e.returncode}): {e.stderr.strip()}")
        except Exception as e:
            logger.error(f"Unexpected error during standalone conversion: {e}")
            raise ConversionError(f"Unexpected conversion error: {e}")

        conversion_time = time.time() - start_time
        logger.info(f"Standalone conversion completed in {conversion_time:.2f}s")

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
