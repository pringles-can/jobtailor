---
name: add-accomplishment
description: Procedure for appending a new accomplishment or job to data/profile.yaml — the full field schema, how to choose an id, how to write a quantified past-tense result, and how to normalize skills tags so filtering works. Use whenever the user wants to record a new accomplishment, role, or job.
---

# Add an accomplishment to `profile.yaml`

`data/profile.yaml` is the single source of truth. Each accomplishment is one
STAR-style entry that the tailoring step filters (on `skills`) and rephrases.

## Field schema

Every accomplishment needs these fields (see `Accomplishment` in
`src/jobtailor/models.py`):

| Field       | Type         | Notes |
|-------------|--------------|-------|
| `id`        | string       | Unique, kebab-case, stable. See below. |
| `employer`  | string       | Company name. |
| `role`      | string       | Title held during this work. |
| `start`     | string       | Free-form date, e.g. `"2021-03"`. Quote it. |
| `end`       | string       | `present` or a date like `"2023-08"`. |
| `situation` | string       | The context / problem. |
| `task`      | string       | What you were responsible for. |
| `action`    | string       | What you actually did. |
| `result`    | string       | The outcome — quantified, past tense (see below). |
| `metrics`   | list[string] | Short numeric facts, e.g. `"p99 1.8s -> 420ms"`. |
| `skills`    | list[string] | Normalized tags used for selection (see below). |
| `phrasings` | list[string] | Pre-written wordings; add 1-3 alternates. |

## Choosing an `id`

- kebab-case, lowercase, short: `pay-latency`, `data-pipeline`.
- Make it descriptive of the accomplishment, not the employer.
- It must be unique across the whole file, and stable — the tailored output
  references it, and `runs/` artifacts are diffed by it. Never renumber existing
  ids.

## Writing `result`

- Past tense, active voice: "Cut", "Rebuilt", "Reduced", "Shipped".
- Quantify it. Prefer a before/after or a percentage: "from 6 hours to 40
  minutes", "+6% conversion". If you truly have no number, state the concrete
  outcome ("shipped to production in three weeks").
- One sentence. Put extra numbers in `metrics`.

## Normalizing `skills` tags

Selection filters on `skills`, so tags must be consistent or filtering misses.

- lowercase, kebab-case: `data-pipelines`, not `Data Pipelines`.
- Prefer an existing tag already used elsewhere in the file over a new synonym
  (grep the file first). Keep `python` vs `py`, `async` vs `asyncio` consistent.
- Tag the transferable skill, not the tool version: `redis`, not `redis-7`.

## Phrasings

- Add at least one; two or three alternates is ideal for high-value entries.
- Each must be truthful and self-contained (readable as a resume bullet on its
  own). Vary emphasis (impact-first vs. action-first) so tailoring has options.

## After editing

Run `uv run pytest` — profile validation is covered by the test suite, and a bad
field (wrong type, missing required key) will fail loudly.
