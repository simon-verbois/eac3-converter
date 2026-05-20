# Changelog

All notable changes to this project are documented here. Format loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/spec/v2.0.0.html).

## [v2.2.0] — 2026-05-20

### Added
- **Standalone audio conversion (opt-in).** Loose `.dts` / `.truehd` files sitting next to a movie (Jellyfin-style external tracks) are now converted to a sibling `<name>.ec3` in a second pass. Enable with `PROCESS_STANDALONE_AUDIO=true`.
- New env vars: `STANDALONE_AUDIO_EXTENSIONS`, `STANDALONE_AUDIO_KEEP_ORIGINAL`, `STANDALONE_AUDIO_OUTPUT_EXTENSION`.
- `ffprobe`-based codec verification before standalone conversion: already-EAC3/AC3 files and unsupported codecs are skipped and cached, so they aren't re-probed every run.
- Unit tests covering the new config keys and the standalone discovery / processing paths (47 tests total).

## [v2.1.0] — 2026-05-20

### Added
- **Dynamic EAC3 bitrate per channel count.** Bitrate is now chosen automatically based on the source stream's channel count, with three tunable env vars: `FFMPEG_BITRATE_STEREO` (≤2ch), `FFMPEG_BITRATE_SURROUND` (3–6ch), `FFMPEG_BITRATE_SURROUND_PLUS` (7+ch).
- `FFMPEG_DIALNORM` and `FFMPEG_MIXING_LEVEL` env vars to control dialog normalization and mixing-level metadata.

### Removed
- Single global `FFMPEG_BITRATE` setting (replaced by the per-channel variants above).

## [v2.0.0] — 2026-05-20

### Added
- **Test suite.** Pytest-based tests for `CacheManager` and the config loader, plus `requirements-dev.txt`.
- Migrated CI from Gitea to Forgejo workflows.

### Changed
- **Cache layer rewritten** for atomic, queryable SQLite-backed persistence.
- **Config loader refactored** into dataclasses with strict env-var parsing and validation (raises a clean `ConfigError` instead of crashing at import time).
- `main.py` reorganised around the new config/cache architecture.
- Kubernetes ConfigMap and Deployment manifests updated to match the new env-var surface.
- README rewritten around the env-var-driven configuration.

## [v1.0.8] — 2025-12-13

### Fixed
- Recursive MKV discovery and small `file_processor` correctness fixes.
- Kubernetes deployment manifest cleanups.

## [v1.0.7] — 2025-12-11

### Changed
- Tighter resource limits / healthcheck in compose and the k8s deployment.

## [v1.0.6] — 2025-12-11

### Removed
- Legacy `config/config.toml.template` (configuration is fully env-var driven).

### Changed
- Promoted Kubernetes `*.yaml.template` files to plain `*.yaml` manifests.

## [v1.0.5] — 2025-12-11

### Changed
- `compose.yaml` polish (env defaults / volume layout).

## [v1.0.4] — 2025-12-11

### Changed
- Reorganised Kubernetes manifests into numbered files (`00-namespace`, `01-pvc`, `02-configmap`, `03-deployment`) and turned them into `.template` variants.
- Removed obsolete flat `configmap.yaml` / `pvc-cache.yaml`.

## [v1.0.3] — 2025-12-11

### Changed
- README polish.

## [v1.0.2] — 2025-12-11

### Changed
- README rewrite.

## [v1.0.1] — 2025-12-11

### Changed
- README rewrite.

## [v1.0.0] — 2025-12-11

### Added
- Initial public release: automatic DTS/TrueHD → EAC3 conversion for MKV files using `ffmpeg`/`ffprobe`.
- Recursive scan of an input directory, scheduled daily run or `RUN_IMMEDIATELY` mode.
- File-level cache to skip already-processed files.
- Disk-space pre-check and configurable ffmpeg timeout / threading / performance flags.
- Structured logging and custom exception hierarchy (`ConversionError`, `ConversionTimeoutError`, `DiskSpaceError`, …).
- Docker image and Kubernetes manifests for production deployment.
