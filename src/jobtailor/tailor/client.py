"""Talks to the Anthropic API and turns its reply into a typed `TailoredResume`.

The prompt instructs Claude to return JSON only. We still defensively strip a
surrounding markdown code fence (```json ... ```) in case the model wraps the
JSON, then parse with `json` + pydantic — no regex, no string surgery on the
actual content.
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic

from jobtailor import config
from jobtailor.models import JobPosting, Profile, TailoredResume

# Prompt files live next to this module. `.parent` is this file's directory.
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / name).read_text(encoding="utf-8")


def _strip_code_fences(text: str) -> str:
    """Remove a surrounding ```json ... ``` (or ``` ... ```) fence if present."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    # splitlines() splits on newlines. Drop the opening fence line, and the
    # closing ``` line if there is one.
    lines = stripped.splitlines()
    lines = lines[1:]  # slice off the first line (``` or ```json)
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]  # slice off the trailing ``` line
    return "\n".join(lines).strip()


def build_prompt(profile: Profile, job: JobPosting) -> str:
    """Assemble the full user-turn prompt from the task template + the data."""
    task = _load_prompt("tailor_task.md")
    # An f-string is Python's string interpolation: C#'s $"{x}" is f"{x}" here.
    # model_dump_json serializes the pydantic model to a JSON string.
    return (
        f"{task}\n\n"
        f"## Job description\n\n{job.description}\n\n"
        f"## Candidate profile (JSON)\n\n{profile.model_dump_json(indent=2)}\n"
    )


def tailor(profile: Profile, job: JobPosting) -> tuple[TailoredResume, str, str]:
    """Call the API and parse the reply.

    Returns a 3-tuple `(result, prompt, raw)` — Python functions return multiple
    values as a tuple. The caller logs all three into `runs/`.
    """
    system = _load_prompt("system.md")
    prompt = build_prompt(profile, job)

    client = anthropic.Anthropic(api_key=config.anthropic_api_key())
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    # response.content is a list of content blocks. This is a generator
    # expression fed to next(): it returns the text of the first text block.
    raw = next(block.text for block in response.content if block.type == "text")

    payload = _strip_code_fences(raw)
    data = json.loads(payload)  # JSON string -> dict, like JsonSerializer.Deserialize
    # model_validate turns the plain dict into a validated TailoredResume.
    result = TailoredResume.model_validate(data)
    return result, prompt, raw
