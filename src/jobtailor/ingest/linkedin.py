"""LinkedIn ingester — STUB. Not implemented in this scaffold.

When implemented, this will fetch the job-posting HTML with `httpx` and parse it
with `selectolax`, returning a `JobPosting`. See the `new-ingester` skill for the
contract it must satisfy. Until then it raises NotImplementedError.
"""

from __future__ import annotations

from jobtailor.models import JobPosting


def fetch(url: str) -> JobPosting:
    # `raise` throws an exception (like C# `throw`). NotImplementedError is the
    # conventional Python way to mark a deliberately-unbuilt code path.
    raise NotImplementedError(
        "LinkedIn ingestion is not implemented yet. "
        "Paste the job description as plaintext, or pass a .txt file, instead. "
        f"(requested URL: {url})"
    )
