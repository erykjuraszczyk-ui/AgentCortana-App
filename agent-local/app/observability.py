import logging

_CONFIGURED = False

def setup_otel_logging(service_name: str = "agentcortana", level: int = logging.INFO):
    """Idempotentne ustawienie logowania (test oczekuje idempotencji)."""
    global _CONFIGURED
    logger = logging.getLogger(service_name)
    if not logger.handlers:
        h = logging.StreamHandler()
        f = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        h.setFormatter(f)
        logger.addHandler(h)
    logger.setLevel(level)
    _CONFIGURED = True
    return logger
