# AgentCortana-App — scaffold

![preflight](https://github.com/erykjuraszczyk-ui/AgentCortana-App/actions/workflows/preflight.yml/badge.svg)

Minimalna aplikacja FastAPI + Docker + GitHub Actions (preflight: tests + docker build).

### Telemetry (optional)
Set `OTEL_ENABLED=1` and provide standard OTLP envs (e.g. `OTEL_EXPORTER_OTLP_ENDPOINT`) to enable OpenTelemetry logs.
Without `OTEL_ENABLED`, telemetry is disabled (safe for local and CI).
