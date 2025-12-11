import logging
import logging.config
import sys
from .config import config


def setup_logging():
    """Set up logging configuration based on debug mode."""

    log_level = logging.DEBUG if config.app.debug_mode else logging.INFO

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[%(asctime)s] %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": sys.stderr
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        },
        "loggers": {
            "eac3_converter": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            }
        }
    }

    logging.config.dictConfig(logging_config)

    # Get logger for this module
    logger = logging.getLogger("eac3_converter")
    logger.info("Logging configured successfully")
    logger.debug(f"Debug mode: {config.app.debug_mode}")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
