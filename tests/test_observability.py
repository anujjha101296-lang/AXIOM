"""Tests for observability layer (logging and metrics)."""

import json
import logging

from axiom.observability.logger import _JsonFormatter, configure_logging, get_logger
from axiom.observability.metrics import METRICS


def test_get_logger_returns_named_logger():
    logger = get_logger("axiom.test.observability")
    assert logger.name == "axiom.test.observability"


def test_json_formatter_outputs_valid_json():
    formatter = _JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="hello world",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    data = json.loads(output)
    assert data["level"] == "INFO"
    assert data["message"] == "hello world"
    assert "timestamp" in data


def test_configure_logging_idempotent():
    configure_logging(level="WARNING", log_format="console")
    configure_logging(level="WARNING", log_format="console")
    root = logging.getLogger()
    assert root.level == logging.WARNING


def test_metrics_counter_increment():
    counter = METRICS.api_requests_total
    before = sum(v for _, v in counter.collect())
    counter.inc(method="GET", endpoint="/test", status="200")
    after = sum(v for _, v in counter.collect())
    assert after >= before + 1


def test_metrics_histogram_observe():
    hist = METRICS.api_request_duration
    hist.observe(0.05)
    data = hist.collect()
    assert data["count"] >= 1
    assert data["sum"] >= 0.05


def test_metrics_prometheus_text_format():
    text = METRICS.prometheus_text()
    assert "axiom_api_requests_total" in text
    assert "# TYPE" in text
    assert "# HELP" in text
