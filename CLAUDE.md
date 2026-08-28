# jobtailor

Takes hand-maintained resume data (`data/profile.yaml`) plus a target job
description, uses the Anthropic API to select and rephrase accomplishments
against that job, and writes a tailored `.docx`.

## Stack (and why each dep is here)
- `uv` — project + dependency manager (like the dotnet CLI + csproj).
- `pydantic` — typed models + validation (like C# records + DataAnnotations).
- `typer` — CLI framework (like System.CommandLine).
- `python-docx` — writes the `.docx` output.
- `anthropic` — Claude API client for tailoring.
- `pyyaml` — reads `profile.yaml` (imported as `yaml`).
- `python-dotenv` — loads secrets from `.env`.
- `httpx` + `selectolax` — reserved for the LinkedIn ingester (unused for now).
- `pymupdf` — reserved for the PDF bootstrap tool (unused for now).
- `pytest` + `ruff` — dev-only: tests and lint/format.

## Architecture rules (do not break)
1. **Dispatcher contract.** `ingest.resolve_job_input(source) -> JobPosting` is
   the only entry for job input: URL -> LinkedIn, existing file -> plaintext,
   `-` -> stdin, else -> the string is the description. Everything downstream
   sees only a `JobPosting`. A new source = one new module + one branch here.
2. **`profile.yaml` is the single source of truth, never a PDF.** The PDF parser
   is a one-time bootstrap that emits YAML to hand-correct; nothing in the
   tailoring path reads a PDF.
3. **Structured JSON from the API.** The prompt demands JSON only; parse it into
   the `TailoredResume` pydantic model. No regex; strip markdown fences first.

## Commands
- Run:  `uv run jobtailor tailor --job-file some.txt`
- Test: `uv run pytest`
- Lint: `uv run ruff check`   Format: `uv run ruff format`

## Conventions
- snake_case names; type hints on all public functions; `_` prefix = internal.
- Every run writes `runs/{timestamp}/` (job text, prompt, raw response, output
  path) so runs can be diffed when output quality changes.
- Secrets live in `.env` (never committed). Copy `.env.example` to `.env`.

## Standing instruction for the author
The author is fluent in C#/.NET and new to Python. Comments should explain
*Python-specific* constructs (decorators, `with`, `__init__.py`, dunder methods,
f-strings, type hints, `None` vs `null`, mutable default args), not general
programming. Prefer boring, explicit code over clever idioms. See the
`python-explainer` skill.
