# Agent-authored output — public summary

The original personal decision record has been retained verbatim in a private
archive. This page is a public summary, not a replacement decision log or a new
authorization grant.

When an agent publishes under a human's identity, attribute agent-written work.
Claim an independent review only when it actually was independent. Do not rely on
transient session URLs as lasting evidence. Lead with the conclusion, link to the
artifact that owns the detail, and avoid repeating the same explanation in every
commit, description and comment.

Publishing permission comes from the current task and applicable instructions,
not from this historical summary.

## Current footer wording

This is the wording agents copy. It is public by nature: it appears on every comment that carries it.

A review comment posted by the reviewing session itself:

```
🤖 Review by Claude Opus 5 — dispatched review session, independent of the session that wrote this PR — via [Claude Code](https://claude.com/claude-code)
```

A review relayed by an orchestrating session:

```
🤖 Findings by a dispatched review session, independent of the session that wrote this PR, relayed and re-checked by the orchestrating session — via [Claude Code](https://claude.com/claude-code)
```

- The footer ends at the `via [Claude Code]` line. There is no session URL, because it does not last.
- The independence clause is a claim. Drop it when the comment is not from an independent session.
- Commits keep `Co-Authored-By` and a `Claude-Session:` trailer.
- A comment that is not review output has no settled footer yet: ask Han first.
