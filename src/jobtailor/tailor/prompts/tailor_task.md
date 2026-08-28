# Task

Tailor the candidate's resume to the job description below.

Select 8-12 entries from `accomplishments`. You may also draw on `projects` —
use the project's `id` and treat its `bullets[].action` as the source material.
Write a 2-3 sentence professional summary aimed at this job, then one tailored
bullet per selected entry.

Return a JSON object with exactly this shape:

{
  "summary": "string",
  "bullets": [
    { "accomplishment_id": "the id from the profile", "text": "the tailored bullet" }
  ]
}

## Timeline continuity

A resume is read as a career history, so an unexplained multi-year hole between
entries is a liability even when the omitted roles are less relevant.

Cover every distinct role (employer + role + date range) held within the last
ten years with at least one bullet. Weight the allocation by relevance: give the
roles that match this job two or three bullets, and roles that match it poorly a
single bullet that surfaces whatever transferable engineering work they contain.
Roles older than ten years may be omitted.

Always include the single most recent role, whatever its relevance. Dropping it
leaves a hole at the top of the timeline, which is the first thing a reader
notices and the hardest to explain away.

Check the dates. If the most recent entry in `projects` starts on or after the
`end` date of the most recent entry in `accomplishments`, the candidate has
ongoing project work covering the period since their last role. In that case
include at least one project bullet, so the resume reads as a continuous
timeline rather than ending at the last employer.

When the job is not a close match for the project's subject matter, still
include it, but frame the bullet around the transferable engineering work —
the languages, data stores, pipelines, and architecture — rather than the
project's domain.

Each `accomplishment_id` must be an `id` that appears in the candidate profile
(either an accomplishment id or a project id). Return JSON only.
