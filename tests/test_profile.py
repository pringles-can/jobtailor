"""Profile/Accomplishment validation fails loudly on bad data."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from jobtailor.models import Accomplishment, Contact, Profile

# Path to the committed example profile, resolved relative to this test file so
# it works no matter which directory pytest is invoked from.
EXAMPLE_PROFILE = Path(__file__).resolve().parents[1] / "data" / "profile.example.yaml"


def _minimal_accomplishment(**overrides):
    """Build a valid Accomplishment kwargs dict, with per-test overrides.

    `**overrides` collects keyword arguments into a dict (like C# params for
    named args); `{**base, **overrides}` merges them, with overrides winning.
    """
    base = dict(
        id="a1",
        employer="Acme",
        role="Engineer",
        start="2020",
        end="2022",
        action="a",
        result="r",
    )
    return {**base, **overrides}


def test_valid_profile_loads():
    profile = Profile(contact=Contact(name="Ada", email="ada@example.com"))
    assert profile.contact.name == "Ada"
    assert profile.accomplishments == []  # default_factory gives a fresh empty list
    assert profile.skill_taxonomy.all_tags() == []


def test_example_profile_is_valid():
    """The committed example must always validate — it's the template users copy."""
    data = yaml.safe_load(EXAMPLE_PROFILE.read_text(encoding="utf-8"))
    profile = Profile.model_validate(data)
    assert profile.contact.name
    assert profile.accomplishments
    assert profile.projects


def test_situation_and_task_may_be_omitted():
    """A freshly bootstrapped profile has no STAR context yet; that's allowed."""
    acc = Accomplishment(**_minimal_accomplishment())
    assert acc.situation is None
    assert acc.task is None


def test_missing_required_field_raises():
    # `id` is required on Accomplishment; leaving it out must raise.
    kwargs = _minimal_accomplishment()
    del kwargs["id"]
    with pytest.raises(ValidationError):
        Accomplishment(**kwargs)


def test_wrong_type_for_metrics_raises():
    # metrics must be a list of strings; a bare string is rejected.
    with pytest.raises(ValidationError):
        Accomplishment(**_minimal_accomplishment(metrics="not-a-list"))


def test_profile_without_contact_raises():
    # contact (with name + email) is the one required block.
    with pytest.raises(ValidationError):
        Profile.model_validate({"summary": "no contact block here"})
