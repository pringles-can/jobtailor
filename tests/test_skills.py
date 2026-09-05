"""The per-role skills line: job-description matching, ordering, and display text.

The load-bearing property is that matching never *adds* a skill — it only sorts
one earlier — so these tests care most about false positives in matching and
about the pool staying exactly what profile.yaml claims.
"""

from jobtailor.render import skills

TAXONOMY = ["csharp", "dotnet", "aspnet-core", "java", "rag", "kafka", "sql-server", "tdd"]
DISPLAY = {
    "csharp": "C#",
    "dotnet": ".NET",
    "aspnet-core": "ASP.NET Core",
    "rag": "RAG",
    "sql-server": "SQL Server",
    "tdd": "TDD",
}


def _matches(tag: str, description: str) -> bool:
    return skills.matches_job(tag, DISPLAY.get(tag, ""), skills.job_tokens(description))


def test_punctuated_job_text_matches_the_slug():
    """ "ASP.NET Core" in the posting must match the tag `aspnet-core`."""
    assert _matches("aspnet-core", "Experience with ASP.NET Core required.")
    assert _matches("sql-server", "Deep SQL Server tuning.")


def test_symbol_heavy_names_match():
    assert _matches("csharp", "Strong C# skills.")
    assert _matches("dotnet", "Building services in .NET 8.")


def test_word_boundaries_prevent_false_positives():
    """The killer case: `rag` must not match inside "storage"."""
    assert not _matches("rag", "Experience with cloud storage systems.")
    assert not _matches("java", "Frontend work in JavaScript.")


def test_singular_posting_matches_plural_tag():
    assert _matches("rest-apis", "Design a REST API.")


def test_matched_tags_sort_first_but_others_survive():
    tags = ["kafka", "csharp", "tdd", "rag"]
    tokens = skills.job_tokens("We want RAG and C# experience.")

    names = skills.skills_for_role(tags, DISPLAY, TAXONOMY, tokens)

    assert names[:2] == ["C#", "RAG"]  # matches, in taxonomy order
    assert set(names[2:]) == {"Kafka", "TDD"}  # the rest still appear


def test_limit_caps_the_line():
    tags = ["csharp", "dotnet", "aspnet-core", "java", "rag", "kafka"]

    names = skills.skills_for_role(tags, DISPLAY, TAXONOMY, set(), limit=3)

    assert len(names) == 3


def test_duplicate_tags_across_accomplishments_collapse():
    names = skills.skills_for_role(["kafka", "kafka", "tdd"], DISPLAY, TAXONOMY, set())

    assert names == ["Kafka", "TDD"]


def test_display_falls_back_to_capitalized_words():
    assert skills.display_name("kafka", {}) == "Kafka"
    assert skills.display_name("event-driven-architecture", {}) == "Event Driven Architecture"
    assert skills.display_name("csharp", DISPLAY) == "C#"
