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
| `FFMPEG_AUDIO_BITRATE` | `640k` | EAC3 output bitrate |
| `FFMPEG_TIMEOUT_SECONDS` | `3600` | Max conversion time per file |
| `FFMPEG_MIN_DISK_SPACE_RATIO` | `1.5` | Required free space multiplier |
| `FFMPEG_THREADS` | `0` | ffmpeg threads (0 = auto) |
| `FFMPEG_STRICT_MODE` | `-2` | ffmpeg strict compliance |
| `FFMPEG_FLAGS` | `+genpts` | ffmpeg input flags |
| `FFMPEG_BUFSIZE` | `128k` | Audio buffer size |
| `FFMPEG_PERFORMANCE_FLAGS` | `+discardcorrupt+genpts+igndts+ignidx` | Corruption/perf flags |
| `FFMPEG_AVOID_NEGATIVE_TS` | `make_zero` | Negative timestamp handling |
| `FFMPEG_MAX_MUXING_QUEUE_SIZE` | `1024` | Mux buffer size |

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

## License

See LICENSE file.

## Disclaimer

This is a personal automation script I use on my home server to convert DTS/TrueHD audio tracks in MKV files. I'm sharing it with the community as-is, without any warranty or guarantee of maintenance.

This project was developed with the assistance of a self-hosted Mistral AI model.
