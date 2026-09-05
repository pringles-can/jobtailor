"""Pick the per-role skills line: which of your own tags to show, and in what order.

Nothing in here can invent a skill. The pool is only the tags already written on
your accomplishments in `profile.yaml`; the job description decides *ordering and
emphasis*, never membership. A false match here can therefore only sort a tag
too early — it can never put a skill on the resume that you didn't claim.
"""

from __future__ import annotations

import re

MAX_SKILLS_PER_ROLE = 10

# Tags whose real-world spelling collapses to something the tag text doesn't
# cover: a job description writes "C#" and ".NET", which reduce to "c" and "net",
# so `csharp` and `dotnet` would never match on their own spelling.
_EXTRA_ALIASES: dict[str, tuple[str, ...]] = {
    "csharp": ("c", "csharp"),
    "dotnet": ("net", "dotnet"),
}


def _collapse(text: str) -> str:
    """Lowercase and drop everything that isn't a letter or digit."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def job_tokens(description: str) -> set[str]:
    """Collapse a job description into a set of its 1-, 2-, and 3-word phrases.

    Building a set of n-grams rather than searching one big collapsed string is
    what preserves word boundaries: the tag `rag` must not match inside
    "sto-rag-e", but `aspnet-core` must still match "ASP.NET Core" (whose bigram
    "ASP.NET" + "Core" collapses to exactly "aspnetcore").

    `set[str]` is a hash set (C#'s HashSet<string>), so membership tests below
    are O(1). The `.` `#` and `+` are kept in the word pattern so ".NET", "C#",
    and "C++" survive as single words before being collapsed.
    """
    words = re.findall(r"[A-Za-z0-9.#+]+", description)
    tokens: set[str] = set()
    for i in range(len(words)):
        for n in (1, 2, 3):
            if i + n <= len(words):
                # words[i : i + n] is a slice — the n words starting at i.
                token = _collapse("".join(words[i : i + n]))
                if token:
                    tokens.add(token)
    return tokens


def _aliases(tag: str, display: str) -> set[str]:
    """Every spelling of one tag that should count as a job-description match."""
    collapsed = _collapse(tag)
    forms = {collapsed, _collapse(display)}
    forms.update(_EXTRA_ALIASES.get(tag, ()))

    # Match "REST API" against the tag `rest-apis`. Guarded on length so short
    # tags that merely end in "s" (`aws`) don't get mangled into "aw".
    if collapsed.endswith("s") and len(collapsed) > 4:
        forms.add(collapsed[:-1])

    forms.discard("")  # a blank display name collapses to the empty string
    return forms


def matches_job(tag: str, display: str, tokens: set[str]) -> bool:
    """True if the target job description mentions this skill in any spelling."""
    # `any(...)` short-circuits on the first True, like LINQ's .Any().
    return any(form in tokens for form in _aliases(tag, display))


def display_name(tag: str, display_map: dict[str, str]) -> str:
    """Turn the slug `aspnet-core` into resume text: "ASP.NET Core".

    `profile.yaml`'s `skill_display` wins; otherwise fall back to capitalizing
    the hyphen-separated words, which is already right for tags like `kafka`
    and `terraform`.
    """
    if tag in display_map:
        return display_map[tag]
    return " ".join(word.capitalize() for word in tag.split("-"))


def skills_for_role(
    tags: list[str],
    display_map: dict[str, str],
    taxonomy_order: list[str],
    tokens: set[str],
    limit: int = MAX_SKILLS_PER_ROLE,
) -> list[str]:
    """Return display-ready skill names for one role, job-description hits first.

    `taxonomy_order` is the canonical vocabulary from `profile.yaml`, used to
    keep the line in a stable, grouped order (languages, then AI, then cloud...)
    instead of whatever order the accomplishments happened to be written in.
    """
    # dict comprehension: tag -> its position in the taxonomy (like ToDictionary).
    position = {tag: i for i, tag in enumerate(taxonomy_order)}

    # set(tags) de-duplicates across the role's accomplishments; the sort key is
    # a tuple, so unknown tags (position = len) fall to the end, alphabetically.
    unique = sorted(set(tags), key=lambda t: (position.get(t, len(position)), t))

    matched = [t for t in unique if matches_job(t, display_map.get(t, ""), tokens)]
    matched_set = set(matched)
    rest = [t for t in unique if t not in matched_set]

    return [display_name(t, display_map) for t in (matched + rest)[:limit]]
