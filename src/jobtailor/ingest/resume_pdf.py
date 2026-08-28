"""Resume PDF bootstrap tool — STUB. Not implemented in this scaffold.

This is a ONE-TIME tool: it will read a PDF resume with `pymupdf` and emit YAML
for you to hand-correct into `data/profile.yaml`. Nothing in the tailoring path
ever reads a PDF — `profile.yaml` is the single source of truth.
"""

from __future__ import annotations

from pathlib import Path


def pdf_to_profile_yaml(pdf_path: Path) -> str:
    raise NotImplementedError(
        "PDF bootstrap is not implemented yet. "
        "Hand-write data/profile.yaml using data/profile.example.yaml as a template. "
        f"(requested PDF: {pdf_path})"
    )
