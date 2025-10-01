import os, sys
from fastapi import APIRouter

# bezpieczny odczyt wersji pakietów
try:
    from importlib import metadata as importlib_metadata
except Exception:  # python<3.8 fallback (niepotrzebny tu, ale zostawmy defensywnie)
    import importlib_metadata  # type: ignore

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/version")
def version():
    ver = os.getenv("APP_VERSION", "0.0.0")
    build = {"git_sha": os.getenv("GIT_SHA", ""), "image": os.getenv("IMAGE", "")}
    py = sys.version.split()[0]
    return {"version": ver, "python": py, "build": build}

def _collect_packages():
    wanted = ["fastapi", "starlette", "uvicorn", "httpx", "pydantic", "pytest"]
    packages = {}
    for name in wanted:
        try:
            packages[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            pass
        except Exception:
            pass
    return packages

@router.get("/introspect")
def introspect():
    ver = os.getenv("APP_VERSION", "0.0.0")
    build = {"git_sha": os.getenv("GIT_SHA", ""), "image": os.getenv("IMAGE", "")}
    runtime = {"python": sys.version.split()[0]}
    env = {
        "APP_VERSION": os.getenv("APP_VERSION", ""),
        "GIT_SHA": os.getenv("GIT_SHA", ""),
        "IMAGE": os.getenv("IMAGE", ""),
        "EXPERIMENTAL_ACT_STREAM": os.getenv("EXPERIMENTAL_ACT_STREAM", ""),
    }
    packages = _collect_packages()
    return {
        "service": "AgentCortana-App",
        "version": ver,
        "build": build,
        "runtime": runtime,
        "env": env,
        "packages": packages,
        "endpoints": ["/health", "/version", "/introspect", "/act", "/act/stream"],
    }
