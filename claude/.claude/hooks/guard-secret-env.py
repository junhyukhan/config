#!/usr/bin/env python3
"""PreToolUse guard: stop Claude from reading REAL secret env files.

Blocks the value of secret env files from ever entering context or a loggable
console, while leaving *.example templates fully readable (their whole purpose).

Wired from ~/.claude/settings.json as a PreToolUse hook on Read|Edit|Grep|Bash.
Reads the hook JSON on stdin. Exit 0 = allow. Exit 2 = deny (stderr is shown to
Claude, explaining why). On any parse error it fails OPEN (exit 0) so a malformed
payload never bricks the session.

What counts as a secret env file (by basename):
  .env, .env.local, .env.hosted, .env.production, .env.production.local,
  duri.env, anything.env, .env.<anything>  ...  EXCEPT anything ending in .example

Read/Edit/Grep: denied if the target path is a secret env file (these always
surface file contents).

Bash: denied only if the command BOTH references a secret env file AND uses a
content-dumping command (cat/grep/sed/head/... or `$(< file)` redirection). This
deliberately still ALLOWS file-to-file handling that never prints the value
(cp/scp/mv/chmod/ls/rm, `docker --env-file`, etc.) so legit secret plumbing works.
"""
import sys
import os
import re
import json


def is_secret_name(name: str) -> bool:
    if name.endswith(".example"):        # templates are always fine
        return False
    if name == ".env":
        return True
    if name.startswith(".env."):         # .env.local, .env.hosted, .env.production...
        return True
    if name.endswith(".env"):            # duri.env, foo.env
        return True
    return False


def path_is_secret(path: str) -> bool:
    return is_secret_name(os.path.basename(path.rstrip("/")))


# A filename token that contains .env, with a trailing non-word boundary so
# "foo.environment" is NOT treated as "foo.env".
ENVFILE = re.compile(r"[\w./~-]*\.env(?:\.[\w-]+)*(?![\w-])")

# Commands that dump file contents to stdout (i.e. into context / logs).
READER = re.compile(
    r"\b(cat|bat|tac|nl|less|more|head|tail|grep|egrep|fgrep|rg|sed|awk|gawk"
    r"|xxd|od|hexdump|strings|jq|printenv|source)\b"
)


# Pipeline / list separators. Splitting the command into segments means a reader
# in ONE segment can't flag a .env that only appears in ANOTHER (e.g.
# `printf x > a.env && ls | grep foo`).
SEG_SPLIT = re.compile(r"\|\||&&|[|;&\n]")


# --- Infisical -------------------------------------------------------------
# Added 2026-09-12, after a dispatched security review found that migrating
# duri's secrets to Infisical had SILENTLY REMOVED a protection this hook used
# to provide. `cat .env.hosted` was blocked; `infisical export`, which prints
# the exact same values to stdout, was not — because every rule above matches a
# *filename*, and Infisical has no file to match. The guard has to follow the
# secrets, not the storage format.
#
# Safe by construction and deliberately NOT matched:
#   infisical export --output-file=PATH   writes to disk, prints nothing
#   infisical secrets set|delete          writes; `set --file=` is the import path
#   infisical run -- <app>                injects into the child's env
#   infisical login | init | vault        no values
INFISICAL_EXPORT = re.compile(r"\binfisical\b[^|;&]*\bexport\b")
INFISICAL_OUTFILE = re.compile(r"--output-file(?:[= ]|$)")
INFISICAL_SECRETS = re.compile(r"\binfisical\b[^|;&]*\bsecrets\b")
INFISICAL_SECRETS_WRITE = re.compile(r"\bsecrets\s+(?:set|delete)\b")
# `infisical run -- env` dumps the injected environment; so do printenv and a
# bare `set`. The wrapped command is the thing that prints, not infisical.
INFISICAL_RUN_DUMPS = re.compile(
    r"\binfisical\b[^|;&]*\brun\b[^|;&]*--\s+(?:env|printenv|set)\b"
)


def infisical_dumps_secret(cmd: str):
    """Why a value, not a bool: the caller reports WHICH command was refused."""
    for seg in SEG_SPLIT.split(cmd):
        if INFISICAL_EXPORT.search(seg) and not INFISICAL_OUTFILE.search(seg):
            return "infisical export (no --output-file)"
        if INFISICAL_SECRETS.search(seg) and not INFISICAL_SECRETS_WRITE.search(seg):
            return "infisical secrets"
        if INFISICAL_RUN_DUMPS.search(seg):
            return "infisical run -- env"
    return None


def _seg_reads_secret(seg: str):
    for m in ENVFILE.finditer(seg):
        name = os.path.basename(m.group(0))
        if not is_secret_name(name):
            continue
        prefix = seg[:m.start()].rstrip()
        if prefix.endswith(">"):    # write target (> .env, >> .env, 2> .env) — NOT a read
            continue
        if prefix.endswith("<"):    # read redirect (cmd < .env, $(< .env)) — a read
            return name
        if READER.search(seg):      # bare arg to a reader command in THIS segment — a read
            return name
    return None


def bash_dumps_secret(cmd: str):
    # A .env is only "dumped" if, within a single pipeline segment, it's read by a
    # reader command or a `<` redirect. Writing to a .env, or a reader in a
    # different segment, does not count.
    for seg in SEG_SPLIT.split(cmd):
        hit = _seg_reads_secret(seg)
        if hit:
            return hit
    return None


def deny_infisical(what: str):
    sys.stderr.write(
        f"BLOCKED: `{what}` prints secret VALUES to stdout, which puts them into "
        f"context or a loggable console. Infisical is the source of truth as of "
        f"2026-09-12, so the old file-based guard does not cover it.\n"
        f"  To move values:   infisical export --output-file=<path>   (file-to-file)\n"
        f"  To see key NAMES: infisical export --output-file=/tmp/x && "
        f"grep -oE '^[A-Z_]+' /tmp/x\n"
        f"  To compare without printing: hash the values inside a script.\n"
    )
    sys.exit(2)


def deny(name: str, how: str):
    sys.stderr.write(
        f"BLOCKED: '{name}' is a real secret env file. {how} would put the secret "
        f"into context or a loggable console. Use the matching *.example file for "
        f"key names, or move the real value file-to-file (cp/scp) without printing it.\n"
    )
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open on malformed input

    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    if tool in ("Read", "Edit", "MultiEdit"):
        p = ti.get("file_path", "")
        if p and path_is_secret(p):
            deny(os.path.basename(p), "Reading it")

    elif tool == "Grep":
        p = ti.get("path", "")
        if p and os.path.isfile(p) and path_is_secret(p):
            deny(os.path.basename(p), "Grepping it")

    elif tool == "Bash":
        cmd = ti.get("command", "")
        hit = bash_dumps_secret(cmd)
        if hit:
            deny(hit, "This command")
        inf = infisical_dumps_secret(cmd)
        if inf:
            deny_infisical(inf)

    sys.exit(0)


if __name__ == "__main__":
    main()
