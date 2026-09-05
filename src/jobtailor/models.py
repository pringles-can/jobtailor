"""Pydantic models — the typed shapes that flow through the whole app.

For a C#/.NET reader: a pydantic `BaseModel` subclass is like a C# record with
DataAnnotations validation baked in. It validates and coerces its fields when
you construct it and raises `ValidationError` if the data doesn't fit — similar
to model binding + validation in ASP.NET, but usable on any plain dict.
"""

# `from __future__ import annotations` makes all type hints in this file lazy
# (stored as strings), so we can reference a type before it's defined and avoid
# import cycles. Harmless and common at the top of model files.
from __future__ import annotations

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Header block for the resume: who you are and how to reach you."""

    name: str
    email: str
    # `str = ""` means optional-with-a-default. Empty string is falsy in Python,
    # so `if contact.phone:` cleanly skips the ones you left blank.
    title: str = ""
    tagline: str = ""
    location: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


class Education(BaseModel):
    credential: str
    institution: str
    # `str | None = None` is "string or null" (C#'s `string?`). Use None when
    # "absent" is meaningfully different from "empty".
    year: str | None = None


class SkillTaxonomy(BaseModel):
    """The canonical skill vocabulary, grouped by category.

    Accomplishment `skills` tags must come from this list — selection filters on
    exact match, so drift here silently breaks it. Every group defaults to empty
    so you can omit any category you don't use.
    """

    languages: list[str] = Field(default_factory=list)
    ai: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    data: list[str] = Field(default_factory=list)
    practices: list[str] = Field(default_factory=list)

    def all_tags(self) -> list[str]:
        """Flatten every category into one list of tags."""
        return [
            *self.languages,
            *self.ai,
            *self.cloud,
            *self.data,
            *self.practices,
        ]


class Accomplishment(BaseModel):
    """One STAR-style accomplishment. This model is load-bearing: selection
    filters on `skills`, and tailoring picks or generates a `phrasings` entry.
    """

    id: str
    employer: str
    role: str
    start: str  # free-form date text, e.g. "2021-03" — intentionally not a date type
    end: str  # "present" is allowed

    # Consulting work is done *for* a client; `None` when you were direct-hire.
    client: str | None = None

    # STAR context. These may be null in a freshly bootstrapped profile (a resume
    # rarely records them), so they're optional — but fill them in: they're what
    # the model uses to judge relevance.
    situation: str | None = None
    task: str | None = None
    action: str
    result: str

    # `list[str]` is the type hint (like List<string>). We must NOT write
    # `metrics: list[str] = []` — a mutable default like `[]` is shared across
    # every instance in Python (the classic "mutable default argument" trap).
    # `Field(default_factory=list)` builds a fresh empty list per instance.
    metrics: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    phrasings: list[str] = Field(default_factory=list)


class ProjectBullet(BaseModel):
    """One line of work within a project, with its own skills tags."""

    action: str
    skills: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """Personal/side project. Same spirit as an Accomplishment but not
    employment, so selection can weight it differently.
    """

    id: str
    name: str
    start: str
    end: str
    stack: list[str] = Field(default_factory=list)
    deployment: str | None = None
    bullets: list[ProjectBullet] = Field(default_factory=list)


class Profile(BaseModel):
    """The candidate's hand-maintained resume data (from profile.yaml)."""

    contact: Contact
    summary: str = ""
    education: list[Education] = Field(default_factory=list)
    skill_taxonomy: SkillTaxonomy = Field(default_factory=SkillTaxonomy)

    # Resume text for each taxonomy tag: {"aspnet-core": "ASP.NET Core"}. Tags
    # are lowercase slugs so filtering can match exactly, which is not how they
    # should *print*. Any tag left out falls back to capitalizing its words.
    skill_display: dict[str, str] = Field(default_factory=dict)

    accomplishments: list[Accomplishment] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)


class JobPosting(BaseModel):
    """The normalized job input. Everything downstream of the dispatcher only
    ever sees this — never a URL, file path, or raw HTML.
    """

    source: str  # where it came from: "plaintext" | "stdin" | "inline" | "linkedin"
    title: str = ""
    company: str = ""
    description: str  # the full job text; this is what tailoring reads


class TailoredBullet(BaseModel):
    """One resume bullet the model selected/rephrased for this job."""

    accomplishment_id: str  # matches an Accomplishment.id (or a Project.id)
    text: str


class TailoredResume(BaseModel):
    """The structured result parsed from the API's JSON reply."""

    summary: str
    bullets: list[TailoredBullet] = Field(default_factory=list)
