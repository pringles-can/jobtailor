"""Plaintext job-description ingester — the one fully implemented path."""

from __future__ import annotations

from pathlib import Path

from jobtailor.models import JobPosting


def from_text(text: str, source: str = "plaintext") -> JobPosting:
    """Wrap raw text in a `JobPosting`."""
    return JobPosting(source=source, description=text.strip())


def from_file(path: Path) -> JobPosting:
    """Read a file and wrap its contents in a `JobPosting`."""
    # Path.read_text is the boring, explicit way to read a whole file to a string.
    text = path.read_text(encoding="utf-8")
    return JobPosting(source="plaintext", description=text.strip())
