---
name: prompt-tuning
description: Procedure for changing anything under src/jobtailor/tailor/prompts/ — how to run the same job description against old and new prompts, what to compare in runs/, and the rule to always capture a before/after. Use when editing prompt files or when the user complains about tailoring output quality.
---

# Tune the tailoring prompts

The prompts live in `src/jobtailor/tailor/prompts/`:

- `system.md` — the assistant's role and hard rules (JSON-only, no invention).
- `tailor_task.md` — the task template and the required JSON shape.

**Never edit a prompt without capturing a before/after.** Prompt changes are
easy to regress and hard to notice.

## The before/after procedure

1. **Pick a fixed job description** you'll reuse for the comparison — a real
   `.txt` file works well. Use the same profile.
2. **Run the current prompts and keep the run folder:**
   ```
   uv run jobtailor tailor --job-file bench-job.txt
   ```
   Note the printed `runs/{timestamp}/` path — that is your "before".
3. **Edit the prompt file(s).**
4. **Run again with the same job and profile.** That is your "after".
5. **Diff the two run folders.** Each holds:
   - `job.txt` — should be identical (proves you compared like for like).
   - `prompt.txt` — the assembled prompt; confirm your edit landed.
   - `response.json` — the raw model output; this is what you actually judge.
   - `output_path.txt` — where the `.docx` went; open both to eyeball them.
   ```
   # PowerShell
   Compare-Object (Get-Content runs/BEFORE/response.json) (Get-Content runs/AFTER/response.json)
   ```

## What to compare in `runs/`

- Did the selected `accomplishment_id`s change, and for the better?
- Is the `summary` more targeted to the job?
- Are bullets still truthful (no invented metrics)? This is the top risk.
- Is the output still valid JSON that parsed cleanly (the run succeeded)?

## Reminder

Keep both run folders until you're confident the change is an improvement. If
output quality later regresses, these before/after snapshots are how you find
which prompt edit caused it.
