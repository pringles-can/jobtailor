"""The dispatcher — the architectural centerpiece.

`resolve_job_input` looks at a single string and decides how to turn it into a
`JobPosting`. Everything downstream (tailoring, rendering) only ever sees a
`JobPosting`, so adding a new job source (Indeed, etc.) means writing one new
ingester module and adding one branch here — nothing else changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

from jobtailor.ingest import linkedin, plaintext
from jobtailor.models import JobPosting


def resolve_job_input(source: str) -> JobPosting:
    """Turn a raw job-source string into a `JobPosting`.

    Routing rules, checked in order:
      - "-"                  -> read the description from stdin
      - looks like a URL     -> LinkedIn ingester (a stub for now)
      - is an existing file  -> read the file as plaintext
      - anything else        -> treat the string itself as the description
    """
    if source == "-":
        text = sys.stdin.read()
        return plaintext.from_text(text, source="stdin")

    # startswith accepts a tuple: true if the string starts with any of them.
    if source.startswith(("http://", "https://")):
        return linkedin.fetch(source)

    path = Path(source)
    if path.is_file():
        return plaintext.from_file(path)

    # Fallback: the argument *is* the job description.
    return plaintext.from_text(source, source="inline")
