from __future__ import annotations
import os, sys
from typing import Any, Dict
__version__ = os.getenv("AGENTCORTANA_APP_VERSION", "0.1.0")
def build_meta() -> Dict[str, Any]:
    return {"git_sha": os.getenv("GIT_SHA", ""), "build_time": os.getenv("BUILD_TIME", ""), "python": sys.version.split()[0]}
