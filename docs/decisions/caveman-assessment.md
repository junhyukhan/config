---
type: Decision
title: caveman — what was taken, and the claim that does not hold up
description: >-
  Took caveman-compress's rules and its validator pattern into the index linter; the
  response-style skill is 49x net-negative here, since 99.5% of tokens are input re-reads and it
  compresses only prose.
status: stable
tags: [config, skills, caveman, compression, tokens, external, measurement]
generated: { by: claude/opus-5, at: 2026-08-29T00:00:00Z }
---

# caveman — what was taken, and the claim that does not hold up

**Status:** DECIDED (2026-08-29). Ideas absorbed; the library itself is **not installed**.

Assessment of [`juliusbrussee/caveman`](https://github.com/juliusbrussee/caveman) against this
workspace. Same shape as [`grill-and-decide-skills.md`](grill-and-decide-skills.md), and the same
verdict pattern — take the ideas, leave the dependency.

## Why — the ask (verbatim)

> **Verbatim (2026-08-29):** "also, for these things, i do want you to consider something like
> https://github.com/juliusbrussee/caveman.
>
> i dont want to use this skill straight up and for everything. i want to gain inspiration from this,
> making use of parts that will be useful for me. im sure there are aspects where we can make use of
> the above."

Said while closing a related fork in the same session:

> **Verbatim (2026-08-29):** "wait but using an index uses the same number of words? is there a point
> of doing that?"

> **Verbatim (2026-08-29, approving the tightened form):** "yes this new rec is better."

## Discussion

### Read as files, not as a summary

Cloned and read directly, per [`artifact-checking.md`](artifact-checking.md) and the precedent in
`grill-and-decide-skills.md`, where a summarised read had mis-shaped one of the two skills being
judged. 19 skills, ~13k lines of markdown, plus a Python compression toolchain.

That mattered here: **the repo's headline claim and its own honesty doc contradict each other**, and
only one of them is reachable from a summary.

### The claim that does not hold up

`skills/caveman/SKILL.md` frontmatter: *"Cuts output tokens 65% (measured)."*

`docs/HONEST-NUMBERS.md`, in the same repo:

| What | Number | How measured |
|---|---|---|
| Output reduction vs default verbose replies | **Not published** | *"Harness exists, but repository has no committed reviewed raw result"* |
| Input reduction from the skill | **0%** | *"It's an output-style instruction"* |
| Input cost the skill **adds** | **~1–1.5k tokens per turn** | SKILL.md rules injected into context |

Verified rather than taken on faith: **`benchmarks/results/` contains nothing but `.gitkeep`.** So
the "(measured)" in the description is not backed by anything in the repo, and the honesty doc says
so plainly.

**This is not a reason to dismiss the project — it is the reason to trust the rest of it.** A repo
that ships a page titled *Honest Numbers*, names the workloads where its own product is
net-negative, and links the issues where users measured a loss, is being more careful than most.
The marketing line is the outlier, not the norm. But the finding is exactly this workspace's own
standing rule — *a summarized read of a source is a lead, not a fact* — and it would have been
missed by reading the README.

### What was taken

**1. The remove/preserve split, as a lint.** `caveman-compress`'s rules are concrete and the right
shape: *remove* articles, filler (just/really/basically/actually/simply), pleasantries, hedging,
connective fluff (however/furthermore/additionally); *preserve exactly* code, URLs, paths, commands,
technical terms, proper nouns, dates, version numbers. Encoded in `repos/docs/generate-index.py`
as `lint_description()`.

**2. The no-invented-abbreviations finding**, which is genuinely counter-intuitive and worth
keeping: *"never invent new abbreviations (cfg/impl/req/res/fn) tokenizer split them same as full
word: zero token saved, reader still decode. Full word cheaper AND clearer."* Same for causal arrows
(`→`) — *"either own token, save nothing."* Both are now blocklists in the linter. Note this
workspace uses `→` freely in prose; that is fine, the rule binds only the eagerly-loaded index.

**3. The validator pattern — the most valuable thing in the repo.** An LLM does the prose rewrite; a
deterministic, zero-token script then checks that headings, code blocks, URLs, paths, and inline
code survived, and the rewrite is only committed if it passes. That is precisely this workspace's
`ops/index.py` / `journal/generate.py` ethos applied to compression, and it is the part that makes
compressing 51 descriptions by hand safe rather than reckless.

Its `validate_headings` even carries the lesson we learned separately in
[`git-workflow.md`](../../../docs/decisions/git-workflow.md) — a check that compared only *counts*
reported "Validation passed" on a run that renamed every heading. Same class of bug: a green check
structurally incapable of firing.

**4. `HONEST-NUMBERS.md` as a document type.** A page that states when the thing loses, with the
issue numbers. Worth imitating anywhere we claim a saving.

**5. The out-of-tree backup detail.** `caveman-compress` writes its `.original.md` backups to
`$XDG_DATA_HOME`, explicitly *"so skill auto-loaders don't re-ingest it as a live file."* Directly
relevant here: a `.original.md` left beside a record would be picked up by both `ops/index.py` and
`docs/generate-index.py` as a record.

### What was left, and why

- **The response-style skill (`caveman`) — not adopted, and measured on this workload rather than
  argued from the upstream issue tracker.** Across 42 local sessions and 10,024 assistant turns
  (`~/.claude/projects/**/*.jsonl`):

  | | tokens | share |
  |---|---|---|
  | input (cache read + creation) | 2,021,940,538 | **99.5%** |
  | output, including thinking | 10,618,152 | 0.5% |
  | …of which actual prose | 394,794 | **0.02%** |

  **That last row is all the skill can touch.** It does not compress thinking tokens (its own
  `HONEST-NUMBERS.md` says so) and it does not compress tool-call JSON, which is 75% of content
  output here. So it addresses 0.02% of the token flow while adding ~1,250 tokens per turn to the
  99.5% side: at its own best-case 65% prose reduction that is ~257k saved against ~12.5M spent,
  **49× net-negative**, and still 4.9× net-negative if the overhead is priced as cached input at
  0.1×. No plausible reduction rate makes it pay.

  The reason is structural: **this workspace does not have a verbosity problem, it has a context
  problem.** 1.94 *billion* cache-read tokens. Output style is not the lever — which is exactly why
  the input-side ideas above were the right half to take.

- **Held against our own artifact — and the artifact lost.** The same yardstick priced an
  `@`-imported `docs/decisions-index.md` at **692k tokens per session, 1.50%** of the 46.2M an
  average session re-reads: 2.3× per turn what this skill was rejected for, and ~360× underwater on
  expected saving. **The eager import was reverted the same day**; the index is now pointed at from
  `AGENTS.md`. Applying a standard to someone else's work and not to your own is how it stops being
  a standard. Full reasoning:
  [`cross-repo-retrieval.md`](../../../docs/decisions/cross-repo-retrieval.md).
- **Compressing prose *files* wholesale — not adopted.** caveman's own `Boundaries` section says it:
  code, comments, commits, docs and memory files stay normal prose, because they are read by humans
  later. Our decision records are exactly that. The eagerly-loaded index is the one artifact where
  the per-turn cost justifies compression, which is why the budget binds there and nowhere else.
- **The plugin, hooks, agents, and the multi-harness profile machinery — not installed.** Same
  reasoning as `grill-and-decide-skills.md`: `repos/` is Han's own projects, each an independent repo
  with its own remote, and a read-only upstream mirror breaks that invariant.
- **The wenyan modes** — genuinely clever, no use here.

### Where the taken parts landed

- `repos/docs/generate-index.py` — `MAX_DESCRIPTION_WORDS`, `INVENTED_ABBREVIATIONS`,
  `BANNED_CHARS`, `FILLER_OPENERS`, and the grounding check, all in `lint_description()`, surfaced
  by `--lint` and in the index's own `# Defects` section.
- The 51 record descriptions, rewritten to one sentence under that budget — 3,268 words to 1,435,
  a **56% reduction**, with the grounding check confirming no description asserts a path or date
  its own record does not contain.

**One honest number of our own**, in the spirit of the page above: the compression made the index
*affordable*, not *free*. Eagerly loading it still takes this workspace's eager layer from 3,270 to
5,608 words — **1.71×**, not the 1.4× first estimated. Both the first estimate and a second one
mid-build were low; the number above is measured with `wc -w` over the four eager files plus the
index, and is corrected here rather than quietly restated.

## Related records

- [`grill-and-decide-skills.md`](grill-and-decide-skills.md) — the precedent: absorb ideas from an
  external skills library, do not clone or install it
- [`artifact-checking.md`](artifact-checking.md) — read the artifact, not a summary; the rule that
  surfaced the unbacked claim above
- [`repos/docs/decisions/cross-repo-retrieval.md`](../../../docs/decisions/cross-repo-retrieval.md)
  — the index this was applied to, and why it is eager
