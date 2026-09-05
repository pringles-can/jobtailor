"""Command-line interface, built with typer.

typer maps Python functions to CLI commands using their type hints — much like
System.CommandLine in .NET. The `@app.command()` decorator (the `@` line above a
function) registers that function as a subcommand; a decorator wraps a function
to add behavior, similar to an attribute + source generator in C#.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import typer
import yaml

from jobtailor import config
from jobtailor.ingest import resolve_job_input
from jobtailor.models import Profile
from jobtailor.render import docx
from jobtailor.tailor import client

# The Typer application object. pyproject's [project.scripts] points at this, so
# the `jobtailor` command runs it.
app = typer.Typer(help="Tailor your resume to a job description and emit a .docx.")


# A no-op callback keeps `tailor` as a named subcommand. Without it, Typer would
# collapse a single-command app so you'd type `jobtailor --job-file ...` instead
# of the intended `jobtailor tailor --job-file ...`.
@app.callback()
def _main() -> None:
    """jobtailor: tailor a resume to a job description."""


def _slugify(text: str) -> str:
    r"""Reduce a name to lowercase hyphen-joined words: "Steven Prindle" -> "steven-prindle".

    `re.sub(pattern, replacement, text)` replaces every match, like Regex.Replace
    in C#. The `r"..."` prefix is a raw string (no backslash escaping), which is
    the normal way to write patterns in Python. `[^\w]+` means "one or more
    characters that are not letters/digits/underscore".
    """
    return re.sub(r"[^\w]+", "-", text.strip().lower()).strip("-")


def _stamped_out_path(stamp: str, run_dir: Path, profile: Profile, out: Path | None) -> Path:
    """Decide where the .docx goes, always prefixing the file name with the run stamp.

    The stamp is the run folder's own name, so a resume that has been copied
    somewhere else still points back at `runs/{stamp}/` for its prompt and raw
    response.
    """
    if out is not None:
        # Keep the caller's directory and extension; only rename the file itself.
        # `Path.with_name` swaps the last path component (like changing just the
        # file name in Path.Combine(dir, newName)).
        return out.with_name(f"{stamp}-{out.name}")
    return run_dir / f"{stamp}-{_slugify(profile.contact.name)}-resume.docx"


def _load_profile(path: Path) -> Profile:
    if not path.is_file():
        raise typer.BadParameter(
            f"Profile not found at {path}. Copy data/profile.example.yaml to "
            "data/profile.yaml and edit it."
        )
    # yaml.safe_load parses YAML into plain dicts/lists; model_validate then
    # turns that into a validated Profile (raising loudly on a bad field).
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Profile.model_validate(data)


# `Optional[Path]` is Path-or-None (Python's None is C#'s null). typer needs the
# real Optional here because the default is None.
@app.command()
def tailor(
    job_file: Path | None = typer.Option(
        None, "--job-file", help="Path to a plaintext job description file."
    ),
    job: str | None = typer.Option(
        None, "--job", help="Job description text, a URL, or '-' to read stdin."
    ),
    profile_path: Path = typer.Option(
        config.DEFAULT_PROFILE, "--profile", help="Path to profile.yaml."
    ),
    out: Path | None = typer.Option(
        None, "--out", help="Output .docx path (defaults to the run folder)."
    ),
) -> None:
    """Tailor the profile against a job description and write a .docx."""
    # Exactly one job source is required. A file path wins if both are given.
    source = str(job_file) if job_file is not None else job
    if not source:
        raise typer.BadParameter("Provide --job-file or --job.")

    profile = _load_profile(profile_path)
    posting = resolve_job_input(source)

    tailored, prompt, raw = client.tailor(profile, posting)

    # Timestamped run directory so runs can be diffed when output quality changes.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = config.RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    out_path = _stamped_out_path(stamp, run_dir, profile, out)
    unmatched = docx.render(profile, tailored, out_path, posting.description)

    # Cache everything about this run for later diffing.
    (run_dir / "job.txt").write_text(posting.description, encoding="utf-8")
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (run_dir / "response.json").write_text(raw, encoding="utf-8")
    (run_dir / "output_path.txt").write_text(str(out_path), encoding="utf-8")

    # The model should only ever cite ids that exist in the profile. If it
    # invents one, say so loudly rather than dropping the bullet silently.
    if unmatched:
        typer.echo(
            f"WARNING: {len(unmatched)} bullet(s) referenced unknown ids and were "
            f"omitted: {', '.join(unmatched)}"
        )

    typer.echo(f"Wrote {out_path}")
    typer.echo(f"Run artifacts in {run_dir}")


# `if __name__ == "__main__":` runs only when this file is executed directly
# (e.g. `python cli.py`), not when it's imported. It's the closest Python has to
# a `static void Main`. The installed `jobtailor` command uses `app` directly.
if __name__ == "__main__":
    app()
