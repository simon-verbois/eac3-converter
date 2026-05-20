<p align="center">
  <a href="https://github.com/simon-verbois/eac3-converter/graphs/traffic"><img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fsimon-verbois%2Feac3-converter&label=Visitors&countColor=26A65B&style=flat" alt="Visitor Count" height="28"/></a>
  <a href="https://github.com/simon-verbois/eac3-converter/commits/main"><img src="https://img.shields.io/github/last-commit/simon-verbois/eac3-converter?style=flat" alt="GitHub Last Commit" height="28"/></a>
  <a href="https://github.com/simon-verbois/eac3-converter/stargazers"><img src="https://img.shields.io/github/stars/simon-verbois/eac3-converter?style=flat&color=yellow" alt="GitHub Stars" height="28"/></a>
  <a href="https://github.com/simon-verbois/eac3-converter/issues"><img src="https://img.shields.io/github/issues/simon-verbois/eac3-converter?style=flat&color=red" alt="GitHub Issues" height="28"/></a>
  <a href="https://github.com/simon-verbois/eac3-converter/pulls"><img src="https://img.shields.io/github/issues-pr/simon-verbois/eac3-converter?style=flat&color=blue" alt="GitHub Pull Requests" height="28"/></a>
</p>

# EAC3 Converter

Automatically converts DTS and TrueHD audio tracks to EAC3 format in MKV files. Optimized for performance and reliability.

## Features

- **Auto-detection** of DTS/TrueHD tracks in MKV files
- **Standalone audio support** (opt-in) for loose `.dts`/`.thd` files alongside videos (e.g. external tracks loaded by Jellyfin)
- **High-performance** ffmpeg conversion with threading
- **SQLite cache** to avoid re-processing files (atomic, fast, queryable)
- **Scheduled processing** or on-demand execution
- **Docker & Kubernetes** ready for production deployment
- **Environment-variable configuration** (12-factor friendly)


## Quick Start

### Configuration

All settings are configured via environment variables. See [compose.yaml](compose.yaml) for the full list with default values.

| Variable | Default | Description |
|---|---|---|
| `TZ` | `Europe/Paris` | System timezone |
| `DEBUG_MODE` | `false` | Verbose logging |
| `START_TIME` | `04:00` | Daily processing time (HH:MM) |
| `RUN_IMMEDIATELY` | `false` | Process once on startup and exit |
| `FFMPEG_BITRATE_STEREO` | `384k` | EAC3 bitrate for 1–2 channel streams |
| `FFMPEG_BITRATE_SURROUND` | `1536k` | EAC3 bitrate for 3–6 channel streams (5.1) |
| `FFMPEG_BITRATE_SURROUND_PLUS` | `1664k` | EAC3 bitrate for 7+ channel streams (7.1) |
| `FFMPEG_DIALNORM` | `-27` | Dialog normalization level (-31..-1) |
| `FFMPEG_MIXING_LEVEL` | `80` | Mixing level metadata (informational) |
| `FFMPEG_TIMEOUT_SECONDS` | `3600` | Max conversion time per file |
| `FFMPEG_MIN_DISK_SPACE_RATIO` | `1.5` | Required free space multiplier |
| `FFMPEG_THREADS` | `0` | ffmpeg threads (0 = auto) |
| `FFMPEG_STRICT_MODE` | `-2` | ffmpeg strict compliance |
| `FFMPEG_FLAGS` | `+genpts` | ffmpeg input flags |
| `FFMPEG_BUFSIZE` | `128k` | Audio buffer size |
| `FFMPEG_PERFORMANCE_FLAGS` | `+discardcorrupt+genpts+igndts+ignidx` | Corruption/perf flags |
| `FFMPEG_AVOID_NEGATIVE_TS` | `make_zero` | Negative timestamp handling |
| `FFMPEG_MAX_MUXING_QUEUE_SIZE` | `1024` | Mux buffer size |
| `PROCESS_STANDALONE_AUDIO` | `false` | Also convert loose audio files (e.g. external `.dts` next to a movie that Jellyfin auto-loads) |
| `STANDALONE_AUDIO_EXTENSIONS` | `dts,thd,truehd,dtshd` | Comma-separated extensions to scan as standalone audio |
| `STANDALONE_AUDIO_KEEP_ORIGINAL` | `false` | Keep the original audio file alongside the converted `.ec3` instead of deleting it |
| `STANDALONE_AUDIO_OUTPUT_EXTENSION` | `ec3` | Output file extension for converted standalone audio |

### Standalone audio files

By default the converter only touches `.mkv` files. If you have **loose audio files** sitting next to your movies (the way Jellyfin auto-loads external tracks — e.g. `Movie.mkv` + `Movie.dts`), set `PROCESS_STANDALONE_AUDIO=true` and they'll be converted to EAC3 in a second pass.

How it works:

- The scanner picks up files matching `STANDALONE_AUDIO_EXTENSIONS` (default `dts,thd,truehd,dtshd`).
- Each file is probed with `ffprobe` first — already-EAC3/AC3 files and unsupported codecs are skipped (and remembered in the cache so they're not re-probed daily).
- DTS / TrueHD files are converted to a sibling `<name>.ec3` (Jellyfin recognises this extension as an external track).
- The original file is **deleted** after a successful conversion. Set `STANDALONE_AUDIO_KEEP_ORIGINAL=true` to keep both side by side.
- Channel-aware bitrate (`FFMPEG_BITRATE_STEREO` / `_SURROUND` / `_SURROUND_PLUS`), `FFMPEG_DIALNORM` and `FFMPEG_MIXING_LEVEL` apply the same way as for in-MKV tracks.

### Start

```bash
git clone <repository-url>
cd EAC3_Converter

# Edit compose.yaml to point at your media folders and tweak env vars
vim compose.yaml

docker compose up
```

## Deployment

- **Docker**: See [compose.yaml](compose.yaml) for production.
- **Kubernetes**: See [k8s-manifest/](k8s-manifest/) for manifests (ConfigMap holds env vars).

## Development

Local build and run with:

```bash
docker compose -f compose-testing.yaml build && docker compose -f compose-testing.yaml up
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the release history.

## License

See LICENSE file.

## Disclaimer

This is a personal automation script I use on my home server to convert DTS/TrueHD audio tracks in MKV files. I'm sharing it with the community as-is, without any warranty or guarantee of maintenance.

This project was developed with the assistance of a self-hosted Mistral AI model.
