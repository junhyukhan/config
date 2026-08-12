# Phone → agent interaction (iPhone as a first-class control surface)

**Status:** in progress — paused 2026-08-13, resume at the trial below

## Resume here

Design is settled through the build-vs-adopt call; **nothing has been installed or changed on the
machine.** No launcher was written, `~/.tmux.conf` is untouched (still the untracked 4-line file at
`~`), `shell/.zshrc` is untouched.

**Next step:** trial Herdr on the Mac —

```sh
curl -fsSL https://herdr.dev/install.sh | sh   # → ~/.local/bin/herdr (already on PATH)
```

The `v0.8.0` macOS arm64 binary's SHA-256 was verified against `herdr.dev/latest.json` on 2026-08-12
(`d53a9f93…c658178`, Mach-O arm64, 17M, ad-hoc signed / **not notarized**). Antigravity is already on
Han's PATH and got native session restore in that release, so the multi-harness claim is testable on
day one without installing anything new.

Answer the open questions at the bottom during the trial, then the verdict goes here — that is also
when the tmux prefix question either revives or dies for good.

## Why — the ask (verbatim)

> **Verbatim (2026-08-11):** "thinking of improving the way i interact with my agents - through my
> iphone."

> **Verbatim (2026-08-11, the actual flow and its pain):** "In order to create new sessions (as we
> frequently edit Claude.md files and other configs that warrant a new session - even new shell), I
> use the terms app on my iPhone to ssh into my Mac, then use tmux then create a Claude session.
> This is done because at times I need to manually edit files (secret files) so having
> terminal/filesystem access is helpful. However the key binds are a PITA on my iPhone. + btw the
> iPhone Claude app doesn't give message suggestions like in Claude code on the terminal which is
> mildly irritating as typing on a phone is much more cumbersome. + improving all this will allow me
> to encorporate other agents/harnesses like codex, Hermes, etc. hopefully."

> **Verbatim (2026-08-11, on the launcher idea):** "I do want more info on L1. Not sure what
> Launchers are. But I like where L1 is headed."

> **Verbatim (2026-08-11, steer — menu shape):** "Hmm actually the majority of our sessions will
> start in repos. Although a pr review session may start in the project directory"

> **Verbatim (2026-08-12, secret editing):** "Regarding the secret editor, perhaps we can have a web
> text editor? Lightweight for simple tasks. The phone has tailscale so security isnt a huge
> concern."

> **Verbatim (2026-08-12, constraint on tmux work):** "Tmux is still used when im on my laptop
> though (though not alot)"

> **Verbatim (2026-08-12, on chat as an interface):** "Not sure. For claude code, the phone app is
> probably much better. Discord probably has its place. But probably not my usual feature design and
> implementation work that requires a lot of back and forth convo"

## Discussion

### The problem, stated precisely

The phone is not missing a *door* — Remote Control, push notifications, the Claude iOS app, and an
installed-but-inert Discord plugin all exist. The problem is that the door Han actually uses (SSH →
tmux → `cd` → `claude`) is the right one — it's the only path that also gives shell and filesystem
access, and the only one that will ever fit Codex or Hermes — but it spends dozens of keystrokes,
many of them modifier chords, before a single word of intent gets typed.

Three separable layers came out of this:

- **L1 — session ceremony.** Getting into a session at all.
- **L2 — tmux for touch.** Chords and keybinds on an iOS soft keyboard.
- **L3 — prompt input.** The "no message suggestions" irritation.
- **(L4) — secret-file editing.** The job that forces the SSH path to exist in the first place.

Han selected L1, L2, and secrets. L3 was deferred but not rejected.

### Findings from the existing setup (2026-08-11)

- `~/.tmux.conf` is **4 lines** (vim pane-selection binds), default `C-b` prefix, **no mouse mode**,
  and is an untracked real file at `~` — not a Stow symlink. Drift outside this repo.
- `shell/.zshrc` (154 lines) has **no session-launcher aliases** — every alias is `ls`/`cd`/`vim`
  cosmetics. Nothing shortens the ceremony.
- The live tmux session was named `0` — ad-hoc, nothing to reattach to by name.

So the ceremony was genuinely unabbreviated. The pain is real, not perceived.

### The launcher design (superseded — see below)

A numbered menu script (`config/scripts/launch.sh`), Stow-managed, auto-run on interactive **SSH**
logins only (never local Ghostty), converting `tmux new -s … -c … && claude` into one keypress.
Decided along the way:

- **Multi-harness front door from the start**, not Claude-only — Han picked this explicitly, since
  folding in Codex/Hermes was the stated point of the whole exercise.
- **Trigger: auto on SSH login only**, `q` as the escape hatch to a plain shell.
- **repos-root is the default, per-repo is tier two** — Han's steer above, which matches
  `repos/AGENTS.md` ("Agentic sessions: launch at this root"). A flat per-repo menu optimizes the
  exception and buries the 90% case. Reshaped so the common path is `ssh` + **Enter**.
- Attach-vs-new decided by the menu, enforcing the workspace's own "never two sessions in the same
  repo" rule instead of relying on memory at 11pm.

**This design is superseded by the Herdr evaluation below.** It is recorded because the *reasoning*
survives — repos-root default, SSH-only trigger, multi-harness-first — and those constraints still
apply to whatever ends up being the front door.

### Build vs. adopt — Herdr (2026-08-12)

Han surfaced two links mid-design: <https://hermes-agent.org/> and <https://herdr.dev>.

An initial summarized read of the landing pages characterized Herdr as early-stage. **That was
wrong**, and checking the artifacts directly (per this repo's `artifact-checking.md` disposition)
reversed the recommendation:

| | Verified |
|---|---|
| Repo | `herdrdev/herdr` — Rust, **Apache-2.0** (relicensed from AGPL-3.0-or-later) |
| Traction | **27,464 stars**, 140 open issues, created 2026-03-27, pushed 2026-08-11 |
| Version | **v0.8.0**, protocol 19 — pre-1.0, iterating fast |
| Install | Prebuilt binary, SHA-256 pinned in `herdr.dev/latest.json`; also `flake.nix` + `justfile` |
| Binary | SHA-256 **verified matching** the manifest; Mach-O arm64, 17M, **adhoc/linker-signed, not notarized** |

What the changelog establishes:

- **Mobile is a first-class surface** — "the same static workspace marks across the sidebar,
  navigator, **and mobile views**".
- **It replaces tmux** rather than sitting beside it (panes, workspaces, tab bar, copy-mode, prefix
  and navigate modes).
- **It already integrates both of Han's links** — "Hermes state now comes from screen detection
  while its plugin reports resumable session identity". It herds Hermes.
- **Native session restore** per harness (Claude Code, Codex, Grok `--resume`, Antigravity, OpenCode,
  Pi) — which dissolves the hand-rolled attach-vs-new logic entirely.
- **Remote attach and headless operation**; detached servers survive SSH logout.
- **Worktree groups** — the exact escape hatch `repos/AGENTS.md` already prescribes for the
  one-session-per-repo rule.

**Decision: adopt, don't hand-roll.** Herdr covers session persistence, multi-harness, attach-vs-new,
remote reconnect, and the working/blocked/idle signal — the last being the one thing tmux
fundamentally cannot provide and the highest-value signal on a phone ("which agent is blocked on
me?"). The proposed 60-line launcher would be a worse subset.

**Risk, accepted knowingly:** pre-1.0 at protocol 19, 4½ months old, and it becomes a daemon sitting
between Han and every agent session. Mitigated by Apache-2.0 source, reproducible Nix builds, and
tmux remaining installed as a zero-cost fallback.

**Consequence for L2:** the tmux prefix question is retired for now. Mouse mode is a straight
improvement on the laptop too, but changing the prefix spends muscle memory on a config that may be
abandoned — and tmux stays on the laptop regardless (Han's constraint above), so nothing should be
made phone-only at the laptop's expense.

### Chat as an interface — scoped, not rejected

Hermes' gateway (Telegram/Discord/Slack/WhatsApp/Signal) and the parked Discord plugin are the same
idea from two directions: a messaging compose box on iOS gives a native keyboard, autocorrect,
dictation, and zero modifier keys, which attacks both stated input complaints by not being a
terminal.

Han's answer draws the line precisely: **chat is for low-bandwidth exchanges** — status, approvals,
"did it deploy" — and **not** for feature design and implementation work "that requires a lot of back
and forth convo". The Claude iOS app stays the main surface for Claude Code; the thing worth fixing
there is input ergonomics, not replacement.

### The secret web editor

Still needed and entirely orthogonal to Herdr — it is the reason the SSH path exists. Han's proposal
is a lightweight web text editor, reachable over the tailnet, on the grounds that Tailscale is the
auth boundary. The pattern is already proven here (`tailscale serve` HTTPS for duri), so this is a
small local service on the Mac, not new infrastructure.

Two constraints to carry into that design:

- **Scope it to an explicit whitelist of secret-file paths**, not "edit any file" — cheap, and keeps
  a browser-reachable arbitrary-file-writer off the dev machine.
- **An agent can build it but cannot test it against real secret files** — verifying output would
  mean rendering values the global `AGENTS.md` rule forbids entering context. Testing goes against
  fixtures; the real-file smoke test is Han's.

## Open questions

- Does Herdr actually displace tmux in practice, on both phone and laptop? (Trial pending.)
- What does the Herdr daemon bind to, and how is its socket API authenticated? Not yet read.
- Is the mobile view self-hosted or a hosted dependency? Not yet confirmed.
- Secret web editor: full design not started.
- L3 (iOS Text Replacement, dictation, short slash commands) — deferred, not rejected.
- What role Hermes plays for Han, beyond Herdr's ability to herd it.
