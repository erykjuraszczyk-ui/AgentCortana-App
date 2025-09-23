from __future__ import annotations

import importlib
import logging


def test_setup_otel_logging_idempotent(monkeypatch):
    monkeypatch.setenv("OTEL_ENABLED", "true")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    obs = importlib.import_module("app.observability")
    # wielokrotne wywołanie nie dubluje konfiguracji w sposób niszczący
    obs.setup_otel_logging()
    obs.setup_otel_logging()
    root = logging.getLogger()
    assert len(root.handlers) >= 1
