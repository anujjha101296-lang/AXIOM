"""
Structured Logging — AXIOM Observability Layer
===============================================
Uses Python's standard `logging` with JSON formatting.
All AXIOM services obtain their logger via `get_logger(__name__)`.

Usage:
    from axiom.observability.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Node ingested", node_id="abc123", node_type="THEOREM")
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields attached via `logger.info("msg", extra={...})`
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "module", "msecs", "message", "msg",
                "name", "pathname", "process", "processName",
                "relativeCreated", "stack_info", "thread", "threadName",
            ):
                log_entry[key] = value
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class _ConsoleFormatter(logging.Formatter):
    """Human-readable coloured formatter for local development."""

    COLOURS = {
        "DEBUG":    "\033[36m",   # cyan
        "INFO":     "\033[32m",   # green
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[35m",   # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelname, "")
        ts = time.strftime("%H:%M:%S", time.gmtime(record.created))
        return (
            f"{colour}[{ts}] {record.levelname:<8}{self.RESET} "
            f"\033[1m{record.name}\033[0m  {record.getMessage()}"
        )


def _build_handler(log_format: str) -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    if log_format == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(_ConsoleFormatter())
    return handler


_configured = False


def configure_logging(level: str = "INFO", log_format: str = "json") -> None:
    """
    Call once at application startup to configure the root logger.
    Subsequent calls to `get_logger` will inherit this configuration.
    """
    global _configured
    if _configured:
        return

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(_build_handler(log_format))
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.  Call `configure_logging()` once at startup
    before using loggers across the application.
    """
    return logging.getLogger(name)
