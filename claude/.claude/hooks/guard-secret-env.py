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


def bash_dumps_secret(cmd: str):
    for m in ENVFILE.finditer(cmd):
        tok = m.group(0)
        if not is_secret_name(os.path.basename(tok)):
            continue
        # secret file referenced — is it in a content-dumping context?
        if (
            READER.search(cmd)
            or re.search(r"<\s*" + re.escape(tok), cmd)   # redirection: cmd < .env
            or "$(<" in cmd                                 # bash read: $(< .env)
        ):
            return os.path.basename(tok)
    return None


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

    sys.exit(0)


if __name__ == "__main__":
    main()
