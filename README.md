# EAC3 Converter

A robust audio processing application that automatically converts DTS and TrueHD audio tracks to EAC3 format in MKV files. Built with performance optimization and reliability in mind.

## Features

- **Automatic Detection**: Scans MKV files for DTS and TrueHD audio tracks
- **High-Performance Conversion**: Optimized ffmpeg with threading and performance flags
- **Intelligent Caching**: Avoids re-processing already converted files
- **Scheduled Processing**: Runs daily at configured time or on-demand
- **Docker Ready**: Containerized with health checks and proper resource limits
- **Kubernetes Support**: Complete K8s manifests for production deployment
- **Configurable**: TOML-based configuration for all settings

## Quick Start

### Docker + Compose

```bash
# Build image
docker build -t eac3-converter .

# Run with volumes
docker run -v ./path/to/mkv/root/dir:/app/input:rw \
           -v ./cache:/app/cache:rw \ # You can use a docker volume for this
           -v ./config:/app/config:ro \
           --cpus=0.5 \
           eac3-converter
```

### Kubernetes 

See [k8s-manifest/README.md](k8s-manifest/README.md) for complete Kubernetes deployment instructions.

### Docker Compose (Development)

```bash
# Clone and build
git clone <repository-url>
cd EAC3_Converter

# Place your MKV files in test_data/ folder
cp your-files/*.mkv test_data/

# Build and run
docker compose -f compose-testing.yaml build && docker compose -f compose-testing.yaml up
```

## Configuration

Edit `config/config.toml`:

```toml
[app]
debug_mode = false

[schedule]
start_time = "04:00"
run_immediately = true

[ffmpeg]
audio_bitrate = "640k"
threads = 0
timeout_seconds = 3600
```

## Requirements

- **ffmpeg** with EAC3 support
- **Python 3.12+**
- **Docker** (optional, for containerized deployment)

## Dependencies

- `tomli==1.2.3` - TOML parser

## Architecture

```
src/
├── audio_processor.py    # ffmpeg operations and audio detection
├── file_processor.py     # File handling and metadata
├── scheduler.py          # Scheduling and main loop
├── cache_manager.py      # Processed files cache
├── config.py            # Configuration management
└── logging_config.py    # Logging setup
```

## Docker Compose Features

- **Auto-build**: Automatic image building from Dockerfile
- **Volume mounts**: Persistent cache and configuration
- **Resource limits**: CPU constrained to 0.5 cores
- **Health checks**: Process monitoring with pgrep

## Kubernetes Features

- **ConfigMap**: Configuration management
- **PersistentVolume**: Cache persistence
- **Health probes**: Liveness and readiness checks
- **Resource management**: CPU and memory limits
- **Namespace isolation**: Dedicated eac3-converter namespace

## Performance Optimizations

- Multi-threaded ffmpeg processing
- Disk space verification before conversion
- Timeout protection against hanging processes
- Intelligent file caching to avoid duplicates
- Optimized ffmpeg flags for better performance

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
