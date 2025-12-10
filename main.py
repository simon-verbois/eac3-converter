import os
import shutil
import time
import subprocess
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

INPUT_DIR = "/app/input"
CACHE_FILE = "/app/cache/converted-files.cache"
START_HOUR = int(os.getenv("START_HOUR", 11))  # Default to 11 if not set
RUN_IMMEDIATELY = os.getenv("RUN_IMMEDIATELY", "false").lower() == "true"  # Default to false
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"  # Default to false

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def load_cache():
    """Load the cache of already processed files."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning(f"Cache file {CACHE_FILE} is corrupted. Creating new cache.")
            return {}
    return {}

def save_cache(cache):
    """Save the cache of processed files."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def has_dts_or_truehd(file_path):
    """Check if the file contains DTS or TrueHD audio tracks using ffprobe."""
    command = [
        "ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a",
        "-loglevel", "error", "-print_format", "json"
    ]

    if DEBUG_MODE:
        logging.debug(f"Running ffprobe command: {' '.join(command)}")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning(f"Failed to analyze audio tracks for {file_path}.")
        return False

    try:
        streams = json.loads(result.stdout).get("streams", [])
    except json.JSONDecodeError:
        logging.error(f"Failed to decode ffprobe output for {file_path}: {result.stdout}")
        return False

    if DEBUG_MODE:
        logging.debug(f"Found {len(streams)} audio streams in {file_path}")
        for i, stream in enumerate(streams):
            logging.debug(f"Stream {i}: codec_name={stream.get('codec_name', 'unknown')}")

    for stream in streams:
        codec_name = stream.get("codec_name", "").lower()
        if codec_name in ["dts", "truehd"]:
            return True
    return False

def convert_audio_tracks(input_file, temp_file):
    """Convert DTS or TrueHD tracks to EAC3."""
    command = [
        "ffmpeg", "-i", input_file, "-hide_banner",
        "-loglevel", "error" if not DEBUG_MODE else "info",
        "-b:a", "640k", "-strict", "-2",
        "-fflags", "+genpts", "-map", "0", "-c:v", "copy", "-c:a", "eac3",
        "-c:s", "copy", temp_file, "-y"
    ]

    if DEBUG_MODE:
        logging.debug(f"Running ffmpeg command: {' '.join(command)}")

    subprocess.run(command, check=True)

def get_file_metadata(file_path):
    """Get file metadata for cache identification."""
    try:
        stat_info = os.stat(file_path)
        metadata = {
            "path": file_path,
            "size": stat_info.st_size,
            "mtime": stat_info.st_mtime,
            "ctime": stat_info.st_ctime
        }

        if DEBUG_MODE:
            logging.debug(f"File metadata for {file_path}: {metadata}")

        return metadata
    except FileNotFoundError:
        logging.error(f"File not found when getting metadata: {file_path}")
        return None

def process_file(file_path, processed_cache):
    """Process a single file, using cache to avoid re-processing."""
    filename = os.path.basename(file_path)
    file_metadata = get_file_metadata(file_path)

    if file_metadata is None:
        return

    file_key = f"{file_path}_{file_metadata['size']}_{file_metadata['mtime']}"

    if DEBUG_MODE:
        logging.debug(f"Processing file: {filename} with key: {file_key}")
        if file_key in processed_cache:
            logging.debug(f"Cache hit for {filename} with key: {file_key}")
        else:
            logging.debug(f"Cache miss for {filename} with key: {file_key}")

    if file_key in processed_cache:
        logging.info(f"Skipping {filename} (already processed according to cache)")
        return

    temp_file = os.path.join(os.path.dirname(file_path), f".temp_{filename}")
    new_file_name = os.path.join(os.path.dirname(file_path), filename)

    if has_dts_or_truehd(file_path):
        try:
            logging.info(f"Converting audio tracks for {filename}...")
            convert_audio_tracks(file_path, temp_file)
            logging.info(f"Conversion completed for {filename}.")
            os.remove(file_path)
            logging.info(f"Original file {filename} deleted from input.")
            os.rename(temp_file, new_file_name)
            logging.info(f"File {filename} renamed successfully.")

            processed_cache[file_key] = {
                "timestamp": datetime.now().isoformat(),
                "action": "converted",
                "original_codecs": "dts_or_truehd"
            }
            save_cache(processed_cache)
        except Exception as e:
            logging.error(f"Failed to convert {filename}: {e}")
            # Clean up the temporary file if conversion fails
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return
    else:
        processed_cache[file_key] = {
            "timestamp": datetime.now().isoformat(),
            "action": "skipped",
            "reason": "no_dts_or_truehd"
        }
        save_cache(processed_cache)
        logging.info(f"No DTS or TrueHD tracks found in {filename}, skipping.")

def main():
    logging.info("Starting watch service...")
    if DEBUG_MODE:
        logging.debug(f"Configuration: INPUT_DIR={INPUT_DIR}, START_HOUR={START_HOUR}, RUN_IMMEDIATELY={RUN_IMMEDIATELY}")

    last_run_date = None
    processed_cache = load_cache()
    logging.info(f"Loaded cache with {len(processed_cache)} entries")

    while True:
        now = datetime.now()

        # Détermine si nous devons exécuter le traitement des fichiers
        should_run = False

        if RUN_IMMEDIATELY:
            logging.info("RUN_IMMEDIATELY is enabled. Processing files regardless of schedule.")
            should_run = True
        elif now.hour >= START_HOUR and (last_run_date is None or last_run_date < now.date()):
            logging.info(f"Current time {now.hour}:{now.minute} is after start hour {START_HOUR}. Starting daily file processing...")
            last_run_date = now.date()
            should_run = True
        else:
            if DEBUG_MODE:
                logging.debug(f"Skipping processing: hour={now.hour}, last_run_date={last_run_date}, current_date={now.date()}")

        # Si nous devons exécuter, traitement des fichiers
        if should_run:
            files_to_process = []
            for root, _, files in os.walk(INPUT_DIR):
                if DEBUG_MODE:
                    logging.debug(f"Scanning directory: {root}, found {len(files)} files")
                for file in files:
                    if file.endswith(".mkv"):
                        files_to_process.append(os.path.join(root, file))

            # Process the list of files to avoid issues with in-place modifications
            for file_path in files_to_process:
                process_file(file_path, processed_cache)

            if not RUN_IMMEDIATELY:
                logging.info("Finishing daily processing...")

        time.sleep(60)

if __name__ == "__main__":
    main()
