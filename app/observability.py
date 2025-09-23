from __future__ import annotations
import logging, os
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

def setup_otel_logging() -> None:
    if os.getenv("OTEL_ENABLED", "false").lower() not in {"1","true","yes"}:
        return
    service = os.getenv("OTEL_SERVICE_NAME", "AgentCortana-App")
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    provider = LoggerProvider(resource=Resource.create({SERVICE_NAME: service}))
    provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(
        endpoint=f"{endpoint}/v1/logs"
    )))

    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    root = logging.getLogger()
    root.setLevel(getattr(logging, os.getenv("OTEL_LOG_LEVEL", "INFO").upper(), logging.INFO))
    # do OTLP
    root.addHandler(handler)
    # + konsola jeśli nie ma
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(logging.StreamHandler())
