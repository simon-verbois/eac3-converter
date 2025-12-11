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
- **Smart caching** to avoid re-processing files
- **Scheduled processing** or on-demand execution
- **Docker & Kubernetes** ready for production deployment
- **TOML configuration** for all settings


## Quick Start

### Configuration

See `config/config.toml.template` for all available options with inline comments explaining each parameter.<br>
And rename the template to `config/config.toml`.

### Start

```bash
# Clone repository
git clone <repository-url>
cd EAC3_Converter

# Edit compose and config with your data
vim compose.yaml
vim config/config.toml

# Build and run
docker compose up
```

## Deployment

- **Docker**: See compose.yaml for production.
- **Kubernetes**: See [k8s-manifest/](k8s-manifest/) for manifests.

## Development

Local build and run with:

```bash
docker compose -f compose-testing.yaml build && docker compose -f compose-testing.yaml up
```

## License

See LICENSE file.

## Disclaimer

This is a personal automation script I use on my home server to convert DTS/TrueHD audio tracks in MKV files. I'm sharing it with the community as-is, without any warranty or guarantee of maintenance.

This project was developed with the assistance of a self-hosted Mistral AI model.
