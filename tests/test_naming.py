"""The output .docx name always carries the run stamp, so a copied resume can be
traced back to the `runs/{stamp}/` folder that produced it.
"""

from pathlib import Path

from jobtailor.cli import _slugify, _stamped_out_path
from jobtailor.models import Contact, Profile

STAMP = "20260904-130310"


def _profile() -> Profile:
    return Profile(contact=Contact(name="Steven Prindle", email="s@example.com"))


def test_default_name_is_stamp_plus_slugified_contact_name(tmp_path: Path):
    path = _stamped_out_path(STAMP, tmp_path, _profile(), None)

    assert path == tmp_path / f"{STAMP}-steven-prindle-resume.docx"


def test_explicit_out_keeps_its_directory_and_extension(tmp_path: Path):
    """--out is honored, but the file name still gets the stamp prefix."""
    requested = tmp_path / "somewhere" / "resume.docx"

    path = _stamped_out_path(STAMP, tmp_path, _profile(), requested)

    assert path == tmp_path / "somewhere" / f"{STAMP}-resume.docx"


def test_slugify_collapses_punctuation_and_case():
    assert _slugify("  Ada  Lovelace-King, Jr. ") == "ada-lovelace-king-jr"
