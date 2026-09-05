"""The renderer must join bullets back to their employer/role/dates."""

from pathlib import Path

from docx import Document

from jobtailor.models import (
    Accomplishment,
    Contact,
    Profile,
    Project,
    ProjectBullet,
    SkillTaxonomy,
    TailoredBullet,
    TailoredResume,
)
from jobtailor.render import docx


def _profile() -> Profile:
    return Profile(
        contact=Contact(name="Ada Lovelace", email="ada@example.com"),
        accomplishments=[
            Accomplishment(
                id="old-job",
                employer="Acme",
                role="Engineer",
                start="2018-01",
                end="2020-05",
                action="a",
                result="r",
            ),
            Accomplishment(
                id="new-job",
                employer="Globex",
                client="BigCo",
                role="Senior Engineer",
                start="2022-03",
                end="present",
                action="a",
                result="r",
            ),
        ],
        projects=[
            Project(
                id="side-thing",
                name="Side Thing",
                start="2023-01",
                end="present",
                stack=["python"],
                bullets=[ProjectBullet(action="built it")],
            )
        ],
    )


def _texts(path: Path) -> list[str]:
    return [p.text for p in Document(str(path)).paragraphs if p.text.strip()]


def test_bullets_render_under_their_employer_and_dates(tmp_path: Path):
    tailored = TailoredResume(
        summary="A summary.",
        bullets=[
            TailoredBullet(accomplishment_id="old-job", text="Did an old thing."),
            TailoredBullet(accomplishment_id="new-job", text="Did a new thing."),
        ],
    )
    out = tmp_path / "r.docx"
    unmatched = docx.render(_profile(), tailored, out)

    assert unmatched == []
    lines = _texts(out)

    # The employer heading carries the client in parentheses, and the meta line
    # carries role + a human-readable date range.
    assert "Globex (BigCo)" in lines
    assert any("Senior Engineer" in ln and "Mar 2022 – Present" in ln for ln in lines)
    assert "Acme" in lines

    # Reverse-chronological: the newer job must appear before the older one.
    assert lines.index("Globex (BigCo)") < lines.index("Acme")

    # Each bullet sits after its own employer heading, not in a flat list.
    assert lines.index("Globex (BigCo)") < lines.index("Did a new thing.")
    assert lines.index("Acme") < lines.index("Did an old thing.")


def test_client_with_its_own_parenthetical_does_not_nest(tmp_path: Path):
    """A client like "Dept. of X (DOX)" must not render as "Acme (Dept. of X (DOX))"."""
    profile = _profile()
    profile.accomplishments[1].client = "Michigan Dept. of Health and Human Services (MDHHS)"

    tailored = TailoredResume(
        summary="",
        bullets=[TailoredBullet(accomplishment_id="new-job", text="Did a thing.")],
    )
    out = tmp_path / "r.docx"
    docx.render(profile, tailored, out)
    lines = _texts(out)

    assert "Globex (Michigan Dept. of Health and Human Services)" in lines
    assert not any("((" in ln or "))" in ln for ln in lines)


def test_project_bullets_get_their_own_section(tmp_path: Path):
    tailored = TailoredResume(
        summary="",
        bullets=[TailoredBullet(accomplishment_id="side-thing", text="Built a thing.")],
    )
    out = tmp_path / "r.docx"
    unmatched = docx.render(_profile(), tailored, out)

    assert unmatched == []
    lines = _texts(out)
    assert "Projects" in lines
    assert "Side Thing" in lines
    # Projects are kept out of the employment section.
    assert "Experience" not in lines


def test_projects_lead_when_more_recent_than_newest_job(tmp_path: Path):
    """Ongoing project work covering a gap must appear before employment.

    The side project starts 2023-01; the newest job starts 2022-03, so the
    Projects section leads and the document reads as one unbroken timeline.
    """
    tailored = TailoredResume(
        summary="",
        bullets=[
            TailoredBullet(accomplishment_id="new-job", text="Did a new thing."),
            TailoredBullet(accomplishment_id="side-thing", text="Built a thing."),
        ],
    )
    out = tmp_path / "r.docx"
    docx.render(_profile(), tailored, out)
    lines = _texts(out)

    assert lines.index("Projects") < lines.index("Experience")


def test_experience_leads_when_newest_job_is_most_recent(tmp_path: Path):
    """With no employment gap, employment comes first as usual."""
    profile = _profile()
    # Push the newest job past the project's start date.
    profile.accomplishments[1].start = "2024-06"

    tailored = TailoredResume(
        summary="",
        bullets=[
            TailoredBullet(accomplishment_id="new-job", text="Did a new thing."),
            TailoredBullet(accomplishment_id="side-thing", text="Built a thing."),
        ],
    )
    out = tmp_path / "r.docx"
    docx.render(profile, tailored, out)
    lines = _texts(out)

    assert lines.index("Experience") < lines.index("Projects")


def test_role_skills_line_includes_unselected_accomplishments(tmp_path: Path):
    """The skills line pools every tag for that role, not just the chosen bullets.

    Two accomplishments share one role; only the first is selected. Kafka lives
    on the *unselected* one and must still appear, while the job description
    pushes the tags it mentions to the front of the line.
    """
    profile = _profile()
    profile.skill_taxonomy = SkillTaxonomy(languages=["csharp"], data=["kafka", "sql-server"])
    profile.skill_display = {"csharp": "C#", "sql-server": "SQL Server"}
    profile.accomplishments[1].skills = ["sql-server"]
    profile.accomplishments.append(
        profile.accomplishments[1].model_copy(
            update={"id": "sibling", "skills": ["kafka", "csharp"]}
        )
    )

    tailored = TailoredResume(
        summary="",
        bullets=[TailoredBullet(accomplishment_id="new-job", text="Did a new thing.")],
    )
    out = tmp_path / "r.docx"
    docx.render(profile, tailored, out, job_description="We need strong C# and Kafka skills.")
    lines = _texts(out)

    # One italic line under the role, matches first, then the rest.
    assert "C#, Kafka, SQL Server" in lines


def test_unknown_id_is_reported_not_silently_dropped(tmp_path: Path):
    tailored = TailoredResume(
        summary="",
        bullets=[TailoredBullet(accomplishment_id="does-not-exist", text="Ghost.")],
    )
    unmatched = docx.render(_profile(), tailored, tmp_path / "r.docx")
    assert unmatched == ["does-not-exist"]
