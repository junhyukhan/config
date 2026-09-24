---
type: Decision
title: New-Mac setup — one core Brewfile, vendor installers where they are recommended
description: >-
  The Brewfile is the core every new Mac gets; apps kept on one machine are just installed there,
  with no second list. Tailscale comes from its own package installer. herdr and zed settings are
  stowed. Runbook: docs/new-mac.md.
status: stable
tags: [config, brew, new-machine, stow, setup]
generated: { by: claude/opus-5.5, at: 2026-09-25T00:00:00Z }
---

# New-Mac setup — one core Brewfile, vendor installers where they are recommended

**Status:** DECIDED (2026-09-25). Runbook: [`../new-mac.md`](../new-mac.md).

## Why — the ask (verbatim)

> **Verbatim (Han, 2026-09-25, the ask):** "i recently got a mac mini. let's examine our configs as well as list up the things we need to setup a new mac"

> **Verbatim (Han, 2026-09-25, on moving to brew):** "yes a lot of tools were installed without brew.. perhaps we should move to brew? what can we move into the config repo?"

> **Verbatim (Han, 2026-09-25, on Tailscale and reinstalling):** "for tailscale, their package installer is recommended so let's do that instead of brew. but should we reinstall the non cask apps so the brew cask versions are installed instead?"

> **Verbatim (Han, 2026-09-25, on reviewing the apps):** "alright we should update the Brewfile. but also let's review the apps since some we don't need.
> like pycharm, antigravity."

> **Verbatim (Han, 2026-09-25, on the review):** "remove ice. what is mas
> gemini-cli not needed.
> keep the vs code extensions.
> 
> but also, a lot of apps, i want to keep on this mac but not on the initial install for a new mac. how should i manage this"

> **Verbatim (Han, 2026-09-25, on a per-device list):** "hmm so the extras i keep for each device and gitignore it?"

> **Verbatim (Han, 2026-09-25, settling it):** "hmm by definition if it's a local copy is there even a point keeping it as a brewfile? when am i really going to be using it? i can just keep the list of apps that i want no matter what in config?"

> **Verbatim (Han, 2026-09-25, final cut):** "no i don't want mas, vorsaint"

## Discussion

### What was found

`setup.sh` already installed the Brewfile, set zsh, stowed every package and installed Herdr. The
gaps were apps installed outside Homebrew, Ghostty and Tailscale among them, and state that exists
only on one machine: `agentlab` with no remote, Claude's memory, three local secret files and the
SSH config.

### Decided

- **The Brewfile is the core, and there is no second list.** A per-device extras Brewfile, tracked
  or gitignored, was proposed and dropped on Han's own reasoning: an app kept on one machine is
  already installed there, so a file that could only reinstall it would never be used. The cost is
  that `brew bundle cleanup` must never run.
- **Out of the Brewfile:** PyCharm and Antigravity, Ice, `gemini-cli`, `helm` and `kustomize` (the
  homelab left k3s), the `bun` and `supabase` taps, and the one-off apps Steam, balenaEtcher, Brave,
  DBeaver and DevToys. They stay installed on this Mac. **In:** Ghostty, Firefox, Chrome, Claude,
  Zed, Raycast, BetterTouchTool, Obsidian, Windscribe, `node`, and `infisical` from its vendor tap.
  The VS Code extensions stay, by Han's call.
- **`mas` and Vorssaint are out**, by Han's call. Amphetamine and Bitwarden are manual App Store
  installs listed in the runbook.
- **Tailscale uses its own package installer**, as Tailscale recommends, and is a runbook step
  rather than a Brewfile line. Both of its casks fetch that same package; the choice is Han's.
- **No reinstalling on this Mac.** All twelve affected casks update themselves, so brew skips them
  on upgrade whoever installed them; brew's value for them is the fresh-machine install, which the
  Brewfile gives. Reinstalling would have downgraded Zed and Claude, and pushed PyCharm across a
  major version. Three matched their cask and can be adopted in place.
- **Stowed:** `~/.config/herdr/config.toml` and `~/.config/zed/settings.json`, as new packages
  stowed `--no-folding`, and `~/.config/git/ignore` in the `git` package. None holds a secret; key
  names were checked before tracking. `gh`'s `hosts.yml`, which holds the GitHub token, is never
  tracked.

### Open

- **What the Mac mini is for.** A replacement main machine needs only the runbook. A second,
  always-on machine also needs power settings, a running Herdr server, and a rule for which machine
  writes to which repo: the "machine-2 role" still open in `agentlab/docs/backlog.md`.
