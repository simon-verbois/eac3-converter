# EAC3 Converter

Automatically converts DTS and TrueHD audio tracks to EAC3 format in MKV files. Optimized for performance and reliability.

## Features

- **Auto-detection** of DTS/TrueHD tracks in MKV files
- **High-performance** ffmpeg conversion with threading
- **Smart caching** to avoid re-processing files
- **Scheduled processing** or on-demand execution
- **Docker & Kubernetes** ready for production deployment
- **TOML configuration** for all settings

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd EAC3_Converter

# Add your MKV files to test_data/
cp your-files/*.mkv test_data/

# Build and run
docker compose -f compose-testing.yaml build && docker compose -f compose-testing.yaml up
```

## Configuration

Edit `config/config.toml`. See `config/config.toml.template` for all available options with inline comments explaining each parameter.

Basic configuration:

```toml
[app]
debug_mode = false

[schedule]
start_time = "04:00"
run_immediately = true

[system]
timezone = "Europe/Paris"

[ffmpeg]
audio_bitrate = "640k"
threads = 0
timeout_seconds = 3600
```

## Requirements

- **ffmpeg** with EAC3 support
- **Python 3.12+**
- **Docker** (for containerized deployment)

## Production Deployment

- **Docker**: `docker build -t eac3-converter .`
- **Kubernetes**: See [k8s-manifest/](k8s-manifest/) for manifests

## Architecture

```
src/
├── audio_processor.py    # Audio detection & conversion
├── file_processor.py     # File handling & caching
├── scheduler.py          # Processing orchestration
├── config.py            # Configuration management
└── exceptions.py        # Custom error handling
```

## License

See LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request
