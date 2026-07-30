# config — docs

**Read this first.** The current state of config, plus an index of everything under `docs/`.

## Status — resume here

<!-- What's true right now, and what to pick up next. This is *state*: rewrite it in place,
     don't append history (history lives in decisions/). -->

_(nothing in progress)_

The `claude/` stow package now carries two workflow skills — `grill` and `decide` — alongside
`sync-repos`. `sync-repos` also reports merged branches at the end of a run (reports only; deleting
stays Han's call).

## Index

- **`decisions/`** — design decisions & specs, one file per topic, each a **verbatim ask +
  Discussion** (copy `decisions/TEMPLATE.md` to start one). The append-only record of *why*
  things are the way they are.
  - [`decisions/chore-commit-carve-out.md`](decisions/chore-commit-carve-out.md) — the narrow
    exception letting an agent commit and push without asking.
  - [`decisions/artifact-checking.md`](decisions/artifact-checking.md) — why "verify against the
    artifact" stays a disposition in `AGENTS.md`, with concrete checks at their points of use.
  - [`decisions/grill-and-decide-skills.md`](decisions/grill-and-decide-skills.md) — what was
    absorbed from `mattpocock/skills`, what was left, and why it became two skills.

<!-- Add state singletons here as the repo grows — one file each, rewritten in place:
- **`roadmap.md`** — phases / what's planned
- **`scope.md`** — what's in and out
- **`data-model.md`** — schema reference
-->
