"""Configuration and secrets loading.

Secrets live in a `.env` file (never committed). `python-dotenv` reads that file
into environment variables, which we then pull with `os.environ`.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# load_dotenv() reads a `.env` file (searching the current dir and parents) and
# populates os.environ. Calling it at import time means any module importing
# `config` gets the env vars loaded. It's safe to call more than once.
load_dotenv()

# `__file__` is this source file's path. `.resolve()` makes it absolute, and
# `.parents[N]` walks up the directory tree:
#   parents[0] = .../src/jobtailor, parents[1] = .../src, parents[2] = repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"  # the `/` operator joins paths (like Path.Combine)
DEFAULT_PROFILE = PROJECT_ROOT / "data" / "profile.yaml"

# The Claude model used for tailoring, kept in one place so it's easy to change.
MODEL = "claude-opus-4-8"


def anthropic_api_key() -> str:
    """Return the API key, or raise a clear error if it isn't set."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return key
