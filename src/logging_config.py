import logging
import logging.config
import sys
from pathlib import Path
from .config import config


def setup_logging():
    """Set up logging configuration based on debug mode."""

    log_level = logging.DEBUG if config.debug_mode else logging.INFO

    # Create logs directory if it doesn't exist
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": sys.stderr
            },
            "file": {
                "class": "logging.FileHandler",
                "level": logging.DEBUG,
                "formatter": "detailed",
                "filename": "/app/logs/eac3_converter.log",
                "encoding": "utf-8"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        },
        "loggers": {
            "eac3_converter": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }

    logging.config.dictConfig(logging_config)

    # Get logger for this module
    logger = logging.getLogger("eac3_converter")
    logger.info("Logging configured successfully")
    logger.debug(f"Debug mode: {config.debug_mode}")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
