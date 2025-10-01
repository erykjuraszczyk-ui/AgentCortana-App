from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "agent-local" / "agent_app" / "app" / "main.py"

if not MAIN.exists():
    raise ImportError(f"Cannot find FastAPI app file at {MAIN}")

spec = spec_from_file_location("agent_local_app_main", str(MAIN))
if spec is None or spec.loader is None:
    raise ImportError("Failed to create module spec for local agent app")

module = module_from_spec(spec)
sys.modules["agent_local_app_main"] = module
spec.loader.exec_module(module)  # type: ignore[attr-defined]

# Udostępnij FastAPI app
app = module.app  # noqa: F401
