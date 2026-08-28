---
name: new-ingester
description: Procedure for adding a job-source ingester (LinkedIn, Indeed, etc.) — the JobPosting contract it must satisfy, where to register it in the dispatcher, the fetch-failure fallback rule, caching requirements, and the test to write. Use when adding support for any new job board or job-input source.
---

# Add a job-source ingester

The dispatcher `resolve_job_input(source) -> JobPosting` in
`src/jobtailor/ingest/__init__.py` is the single entry point. Adding a source is
**one new module + one new branch** — nothing downstream changes.

## The `JobPosting` contract

Your ingester must return a `JobPosting` (see `src/jobtailor/models.py`):

- `source`: a short tag for where it came from, e.g. `"linkedin"`, `"indeed"`.
- `description`: the full job text. **Required and non-empty** — this is the
  only field tailoring reads.
- `title`, `company`: fill them if you can parse them; otherwise leave `""`.

Downstream code must never need to know which ingester ran.

## Steps

1. **Create `src/jobtailor/ingest/<source>.py`** with a function that takes the
   raw input (usually a URL) and returns a `JobPosting`. Follow `plaintext.py`
   for shape.
2. **Register one branch in the dispatcher.** Add the routing test (e.g. a
   domain check for the URL) in `resolve_job_input`, calling your new function.
   Keep the ordering sensible (most specific match first).
3. **Fetch with `httpx`, parse with `selectolax`** (both already dependencies).

## Fetch-failure fallback (required)

Network fetches fail — sites block bots, change markup, or time out. On **any**
fetch or parse failure, do not crash with a raw stack trace. Raise a clear error
that tells the user to paste the description as plaintext instead:

    raise RuntimeError(
        "Couldn't fetch the LinkedIn posting (it may require login). "
        "Paste the job description with --job \"...\" or pass a .txt file."
    )

The plaintext path always works, so it is the universal fallback.

## Caching (required)

Cache fetched raw job text under `runs/{timestamp}/` alongside the other run
artifacts (the CLI already writes `job.txt`). If your ingester fetches remote
HTML, also save the raw HTML you fetched so a parse can be re-debugged without
re-hitting the network.

## Test to write

Add a routing test to `tests/test_dispatcher.py` proving the dispatcher sends
the right input to your ingester. **Mock the network** — no test may make a real
HTTP request. Assert on `posting.source` and that `posting.description` is
populated. Mirror `test_url_routes_to_linkedin_stub`.
