# jobtailor

Tailor your resume accomplishments to a specific job description and get a
tailored `.docx` out.

## Install

```
uv sync
```

## Configure

```
# PowerShell (Windows):
Copy-Item .env.example .env
Copy-Item data/profile.example.yaml data/profile.yaml

# bash/macOS/Linux:
cp .env.example .env
cp data/profile.example.yaml data/profile.yaml
```

Then edit `.env` and set `ANTHROPIC_API_KEY`, and edit `data/profile.yaml` with
your real accomplishments (start from the committed example).

## Run

```
uv run jobtailor tailor --job-file some-job.txt
```

This selects and rephrases your accomplishments against the job and writes a
tailored resume `.docx`, plus a timestamped `runs/{timestamp}/` folder holding
the resolved job text, the assembled prompt, and the raw API response (so you
can diff runs when output quality changes).

Other job inputs:

```
uv run jobtailor tailor --job "paste the description here"
echo "job text" | uv run jobtailor tailor --job -
```

## Develop

```
uv run pytest        # tests (the API is mocked; no network calls)
uv run ruff check    # lint
uv run ruff format   # format
```
