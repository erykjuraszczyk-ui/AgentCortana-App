from __future__ import annotations

import os
import platform
from importlib import metadata
from typing import Any
from fastapi import APIRouter
from ..version import __version__, build_meta

router = APIRouter(tags=["meta"])

ALLOWED_ENV_PREFIXES = ("CORTANA_", "OTEL_", "APP_ENV", "ENV", "DEPLOYMENT_ENV")
CORE_PACKAGES = ("fastapi", "uvicorn", "pydantic", "httpx")

def _filtered_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in os.environ.items():
        if k.startswith(ALLOWED_ENV_PREFIXES) or k in ALLOWED_ENV_PREFIXES:
            out[k] = v
    return out

def _pkg_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in CORE_PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pass
    return versions

@router.get("/introspect", summary="Runtime/build/env information (safe)")
async def introspect() -> dict[str, Any]:
    return {
        "service": "AgentCortana-App",
        "version": __version__,
        "build": build_meta(),
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "env": _filtered_env(),
        "packages": _pkg_versions(),
    }
