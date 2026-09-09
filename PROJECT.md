# Ireland Weather Dashboard

<!--
The project's manifest. The ecosystem's session-start hook injects this file
into every agent session bound to this project, so it is the first thing an
arriving agent knows. Keep it a statement of what is true NOW — rewrite stale
lines in place, never append a dated section.
-->

**Repo:** `~/ai/projects/ireland-weather-dashboard/repo` — github.com/FB-QA/ireland-weather-dashboard
**Live:** none.
**Status:** dormant since February 2026.

## What it is

A weather dashboard for Ireland. `docs/spec.md` and `docs/status.md` carry the
original specification and where the build reached.

## Stack

Python (`main.py`, `requirements.txt`) with static assets under `static/` and
tests under `tests/`.

## Two things an arriving agent must know

1. **`main` carries only the initial commit.** The actual application lives on
   the unmerged `feature/initial-build` branch. Do not conclude from `main`
   that nothing was built.
2. **The repo is nested at `repo/`.** The project directory is a container, not
   the repo, which is why `--project ireland-weather-dashboard` cannot yet
   provision a worktree. Flattening it is outstanding work.

## Where things are

| What | Where |
|---|---|
| Specification and build status | `docs/spec.md`, `docs/status.md` |
| Design | `docs/design/` |
| Everything else | the scaffolded `docs/` types, currently empty |

## Open

Nothing in progress. Whether this project resumes at all is undecided.
