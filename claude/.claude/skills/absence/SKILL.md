---
name: absence
description: Before reporting that something is missing, unused, not configured, or not there — prove the probe could have found it. Use whenever a grep, log read, query, scan, port check or ls comes back empty or fails — an error, a missing path, a non-zero exit — and that result is about to become a claim, a recommendation to delete or disable, or evidence that a thing does not exist.
---

# Absence

**An empty result is a claim about the world. It is only as good as proof that the instrument
could have returned something.**

A null from a tool pointed at the wrong layer looks exactly like a null from a tool pointed at
the right one. There is no tell. Which means the moment you are about to write *"there's nothing
there"*, the finding is not the empty output — the finding is the empty output **plus** evidence
that this probe finds things when they exist.

This extends Han's global rule (`config/claude/.claude/AGENTS.md`, *"Verify against the artifact"*):
*"This bites hardest on absence."* That rule is usually read as being about **summarised
documents**. It applies just as hard to **empty command output**, which is the form that keeps
getting through.

## The procedure

Four steps. It costs one extra command.

1. **Say the claim out loud.** "Gerbera has no clients." "The URL carries no `sslmode`." Absence
   claims are load-bearing — they are what justifies deleting, disabling, or concluding a thing
   was never built.
2. **Name the instrument and what it can actually see.** `journalctl -u X` sees systemd units. It
   cannot see containers. `pg_stat_ssl` sees the backend you are attached to — through a pooler,
   that is the pooler's backend, not yours.
3. **Find a known positive and run the probe against it.** Something you are certain exists. If
   the probe finds that, it can find yours. If it does not, your null means nothing and you have
   just saved yourself the wrong conclusion.
4. **Only then report.** If you could not validate, say *"I could not verify this is absent"* —
   which is a different sentence from *"it is absent"*, and the difference is the whole skill.

## What a misaimed instrument looks like

Real cases, all from one session (2026-09-14). Three of the four were repeats *after* the pattern
had been written down, which is why this is a skill and not a paragraph.

| Probe | Read as | Actually |
|---|---|---|
| `journalctl -u gerbera` → empty | "no clients in 30 days; safe to remove" | Gerbera is a **container**. No unit exists, so the null was guaranteed regardless of truth. Acting on it would have killed a documented service. |
| `select ssl from pg_stat_ssl` → `false` | "the connection is unencrypted" | Ran through **Supavisor**. Described the pooler→Postgres hop inside AWS, not ours. Nearly caused a correct security fix to be abandoned as broken. |
| `grep -c 'sslmode=verify-full'` → `0` | "the URL carries no sslmode" | Rules out **one value**, not the parameter. `sslmode=require` would have passed the same grep. |
| `nc -z host 5353` → fail | "mDNS is firewalled" | `nc -z` probes **TCP**; mDNS is **UDP only**. The probe could never have succeeded. mDNS was working. |

The shared shape: **the probe answered a different question than the one being asked**, and
answered it confidently.

## The classes worth memorising

- **Wrong layer.** A proxy, pooler, load balancer or CDN answers about *its* connection, not yours.
- **Wrong mechanism.** systemd vs container vs launchd vs cron. A service absent from one is
  routine in another.
- **Wrong protocol.** TCP probe of a UDP service. HTTP probe of something that speaks a raw
  protocol. `ping` where ICMP is dropped by policy.
- **Wrong scope.** Grep for one *value* when the question is about the *parameter*. Grep one
  directory when the thing lives in a sibling. A pathspec that silently matches nothing.
- **Wrong tree.** Searching the working tree for something that only exists in history, on another
  branch, or in a generated artifact.
- **Reachability vs binding.** `ss -tln` on a host shows what **binds**; it never shows what is
  **reachable**. A firewall makes those two differ, and only a probe from outside sees it.

## Absence is also a reason to open the source of truth

Before concluding that a service, flag or feature "isn't configured" or "isn't used" — and
**always** before recommending it be removed, disabled or firewalled off — grep the repo's own
declared source of truth for its name (`SPEC.md`, `constitution.md`, `docs/decisions/`, the
compose file). A thing can be absent from every runtime probe you ran and still be deliberate,
documented, and load-bearing.

Twice in one session a service was nearly disabled because a *plan* file said it was undocumented,
while the repo's `SPEC.md` documented it with the rationale spelled out. A derived doc is not the
source of truth, and a precise-looking line citation next to a claim is not evidence *for* that
claim — check the claim, not just the quote.

## When you are wrong about absence, say which probe misled you

Not "I was wrong" — **"`journalctl -u gerbera` returned nothing because gerbera is a container."**
The instrument is the reusable part of the correction. Naming it is what stops the next session
reaching for the same tool on the same class of question.
