"""Dispatcher routing: each input type reaches the right ingester."""

from pathlib import Path

import pytest

from jobtailor.ingest import resolve_job_input
from jobtailor.models import JobPosting


def test_existing_file_routes_to_plaintext(tmp_path: Path):
    # tmp_path is a pytest fixture: a fresh temp directory per test.
    f = tmp_path / "job.txt"
    f.write_text("We need a backend engineer.", encoding="utf-8")

    posting = resolve_job_input(str(f))

    assert isinstance(posting, JobPosting)
    assert posting.source == "plaintext"
    assert "backend engineer" in posting.description


def test_inline_string_routes_to_inline():
    posting = resolve_job_input("Senior Python developer wanted.")
    assert posting.source == "inline"
    assert "Python developer" in posting.description


def test_stdin_routes_to_stdin(monkeypatch):
    import io

    # Replace sys.stdin with a fake stream so "-" reads our text, not the console.
    monkeypatch.setattr("sys.stdin", io.StringIO("Job from stdin"))
    posting = resolve_job_input("-")
    assert posting.source == "stdin"
    assert posting.description == "Job from stdin"


def test_url_routes_to_linkedin_stub():
    # The LinkedIn ingester is a stub that raises NotImplementedError; that the
    # exception propagates proves the URL was routed there.
    with pytest.raises(NotImplementedError):
        resolve_job_input("https://www.linkedin.com/jobs/view/123")
