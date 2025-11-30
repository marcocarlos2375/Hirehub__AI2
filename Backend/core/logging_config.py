"""
Logging configuration using Loguru.
Provides structured logging with file rotation and multiple output formats.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Remove default handler
logger.remove()

# Determine log level from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging(
    level: str = LOG_LEVEL,
    serialize: bool = False,
    log_file: bool = True
) -> None:
    """
    Configure Loguru logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        serialize: If True, output JSON format (useful for log aggregation)
        log_file: If True, also log to rotating file
    """
    # Console handler with color formatting
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if serialize:
        # JSON format for production/log aggregation
        logger.add(
            sys.stderr,
            format="{message}",
            level=level,
            serialize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stderr,
            format=console_format,
            level=level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )

    # File handler with rotation
    if log_file:
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level:<8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

        logger.add(
            LOGS_DIR / "hirehub_{time:YYYY-MM-DD}.log",
            format=file_format,
            level=level,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True
        )

        # Separate error log for critical issues
        logger.add(
            LOGS_DIR / "hirehub_errors_{time:YYYY-MM-DD}.log",
            format=file_format,
            level="ERROR",
            rotation="50 MB",
            retention="60 days",
            compression="gz",
            backtrace=True,
            diagnose=True
        )


def get_logger(name: str = None):
    """
    Get a logger instance with optional context binding.

    Args:
        name: Module name for context (auto-detected if None)

    Returns:
        Bound logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logging on import
setup_logging()

# Export for convenience
__all__ = ['logger', 'setup_logging', 'get_logger']
