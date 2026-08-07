#!/usr/bin/env python3
"""PostToolUse hook: format the file Claude just wrote, in repos that opted in.

Wired from ~/.claude/settings.json as a PostToolUse hook on Edit|Write|MultiEdit.
Reads the hook JSON on stdin. Always exits 0 — a formatter is a convenience and
must never break a session or block a write that already succeeded.

Why this exists
---------------
Format drift is created one edit at a time and then cleaned up in bulk: duri-v3
reached `pnpm format:check` red across **65 files**, including files no recent
change had touched, which turns every feature diff into a choice between leaving
drift or sweeping 60 unrelated files into a review. Fixing it at the source is
cheaper than the recurring cleanup commit.
(`repos/docs/decisions/ops-modernization.md`, finding ②.)

Opt-in is by CONFIG, not by binary
----------------------------------
A repo is formatted only if it has *both* a formatter binary and that formatter's
own config file. This distinction is load-bearing: `jhkn-dev` ships a prettier
binary in node_modules (transitively, via Astro) but has **no prettier config** —
formatting it would impose a style the repo never chose, on a global hook the
author of that repo never opted into. Binary-presence is availability; config
presence is consent.

Current effect, measured 2026-08-06:
  duri-v3  → prettier (.prettierrc.json + node_modules/.bin/prettier)
  quant    → ruff     (pyproject.toml [tool.ruff] + .venv/bin/ruff)
  jhkn-dev → SKIPPED  (prettier binary, no config)
  homelab, config → skipped (no formatter)

Known trade, accepted
---------------------
If the formatter rewrites the file, Claude's in-context copy is momentarily
stale, so a follow-up Edit built on the pre-format text can fail to match. That
is a self-correcting failure (re-read and retry) and is the standard cost of
format-on-save; it is called out here so it is recognised rather than debugged.

Deliberately silent: exit 0 with no output, even when the file changed. Emitting
an advisory back to Claude would need the PostToolUse structured-output schema,
which was NOT verified when this was written — do not add it by guessing.
"""
import json
import os
import subprocess
import sys

TIMEOUT_S = 10

# Extensions ruff owns. Everything else falls through to prettier, which is given
# --ignore-unknown so an unsupported extension is a no-op rather than an error.
PY_EXTS = {".py", ".pyi"}

PRETTIER_CONFIGS = (
    ".prettierrc", ".prettierrc.json", ".prettierrc.yaml", ".prettierrc.yml",
    ".prettierrc.json5", ".prettierrc.js", ".prettierrc.mjs", ".prettierrc.cjs",
    ".prettierrc.toml", "prettier.config.js", "prettier.config.mjs",
    "prettier.config.cjs",
)


def repo_root(path):
    """Nearest ancestor containing .git. None if the file is not in a repo."""
    d = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _first_existing(root, names):
    for n in names:
        p = os.path.join(root, n)
        if os.path.exists(p):
            return p
    return None


def ruff_cmd(root):
    """(binary, config) for ruff, or None. Config = ruff configured in this repo."""
    pyproject = os.path.join(root, "pyproject.toml")
    configured = False
    if os.path.exists(pyproject):
        try:
            with open(pyproject, encoding="utf-8", errors="replace") as f:
                configured = "[tool.ruff" in f.read()
        except OSError:
            return None
    if not configured and not os.path.exists(os.path.join(root, "ruff.toml")):
        return None
    binary = os.path.join(root, ".venv", "bin", "ruff")
    return binary if os.path.isfile(binary) and os.access(binary, os.X_OK) else None


def prettier_cmd(root):
    """Local prettier binary, but only if this repo carries a prettier config."""
    if not _first_existing(root, PRETTIER_CONFIGS):
        return None
    binary = os.path.join(root, "node_modules", ".bin", "prettier")
    return binary if os.path.isfile(binary) and os.access(binary, os.X_OK) else None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open on malformed input, exactly like guard-secret-env

    if data.get("tool_name") not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not os.path.isfile(path):
        sys.exit(0)

    root = repo_root(path)
    if not root:
        sys.exit(0)

    ext = os.path.splitext(path)[1].lower()
    if ext in PY_EXTS:
        binary = ruff_cmd(root)
        argv = [binary, "format", path] if binary else None
    else:
        binary = prettier_cmd(root)
        # --ignore-unknown: a .lua or .sh edit in a prettier repo is a no-op, not
        # an error. --log-level=silent keeps a successful run from printing.
        argv = [binary, "--write", "--ignore-unknown", "--log-level=silent", path] if binary else None

    if not argv:
        sys.exit(0)

    try:
        subprocess.run(
            argv, cwd=root, timeout=TIMEOUT_S,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
    except Exception:
        pass  # a formatter failing is never worth interrupting the session

    sys.exit(0)


if __name__ == "__main__":
    main()
