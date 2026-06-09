"""Load .env file from HUNT-AGENT root + validate API keys."""

from __future__ import annotations

import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def _load_dotenv(path: Path = ENV_PATH) -> dict[str, str]:
    if not path.exists():
        return {}
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip("\"'")
    return env


ENV = _load_dotenv()
SERPAPI_KEY = ENV.get("SERPAPI_KEY", "")
SEARCHAPI_KEY = ENV.get("SEARCHAPI_KEY", "")


def validate_api_keys():
    if not SERPAPI_KEY and not SEARCHAPI_KEY:
        print(
            "FATAL: No API key found. Set SERPAPI_KEY or SEARCHAPI_KEY in .env",
            file=sys.stderr,
        )
        sys.exit(1)
    if not SERPAPI_KEY:
        print("  [env] SERPAPI_KEY not set — will fall back to SearchAPI.io")
    if not SEARCHAPI_KEY:
        print("  [env] SEARCHAPI_KEY not set — will use SerpAPI only")
