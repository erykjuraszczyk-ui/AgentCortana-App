from __future__ import annotations

import logging
import os
from typing import Final


def setup_otel_logging() -> None:
    """
    Configure OpenTelemetry logging if:
      - OTEL_ENABLED is true-ish
      - OTel packages are available

    Idempotent: wielokrotne wywołania nie powinny dublować handlerów konsolowych.
    """
    enabled = os.getenv("OTEL_ENABLED", "false").lower() in {"1", "true", "yes"}
    if not enabled:
        return

    # Leniwy import OTel dopiero, gdy feature flag włączony
    try:
        # isort: off  # ruff I001 – nie sortować i nie przenosić tych importów
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs import LoggingHandler, LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        # isort: on
    except Exception:  # brak paczek albo inny runtime issue -> po prostu wyjdź
        return

    service: Final[str] = os.getenv("OTEL_SERVICE_NAME", "AgentCortana-App")
    endpoint: Final[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    provider = LoggerProvider(resource=Resource.create({SERVICE_NAME: service}))
    provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs"))
    )

    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    root = logging.getLogger()
    root.setLevel(getattr(logging, os.getenv("OTEL_LOG_LEVEL", "INFO").upper(), logging.INFO))

    # OTLP handler
    root.addHandler(handler)
    # Konsola (jeśli nie ma)
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(logging.StreamHandler())
