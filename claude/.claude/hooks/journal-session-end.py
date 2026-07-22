#!/usr/bin/env python3
"""SessionEnd hook: append a one-line stub for this session to the work journal.

Journal layout: ~/workdir/repos/journal/YYYY/YYYY-Www.md (ISO week, one file per
week, append-only). Each line: timestamp, repo, first real user ask (truncated),
session id. Zero agent tokens — this runs as a plain script after the session ends.

Fail-silent by design: a journal miss must never break a session. The transcript
is read only to pull the FIRST user prompt; nothing else leaves it.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

JOURNAL_ROOT = Path.home() / "workdir" / "repos" / "journal"
REPOS_ROOT = Path.home() / "workdir" / "repos"
MAX_ASK_LEN = 140


def first_user_ask(transcript_path):
    """First real (typed) user message in the transcript, or None."""
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "user" or obj.get("isMeta"):
                    continue
                content = (obj.get("message") or {}).get("content")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
                    )
                if not isinstance(content, str):
                    continue
                text = content.strip()
                # skip harness-injected wrappers, slash-command envelopes, resume caveats
                if not text or text.startswith(("<", "Caveat:")):
                    continue
                text = re.sub(r"\s+", " ", text)
                if len(text) > MAX_ASK_LEN:
                    text = text[: MAX_ASK_LEN - 1] + "…"
                return text
    except OSError:
        pass
    return None


def repo_label(cwd):
    """First path component under ~/workdir/repos, or the cwd basename."""
    try:
        rel = Path(cwd).resolve().relative_to(REPOS_ROOT)
    except ValueError:
        return Path(cwd).name or "?"
    return rel.parts[0] if rel.parts else "repos"


def main():
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "")
    ask = first_user_ask(data.get("transcript_path", ""))
    if not ask:  # no real user prompt -> trivial session, skip
        return

    if not JOURNAL_ROOT.parent.is_dir():  # machine without the workspace checkout
        return

    now = datetime.now()
    week_file = JOURNAL_ROOT / now.strftime("%G") / (now.strftime("%G-W%V") + ".md")
    week_file.parent.mkdir(parents=True, exist_ok=True)

    short_id = session_id[:8] or "unknown"
    if week_file.exists() and short_id in week_file.read_text(encoding="utf-8"):
        return  # SessionEnd can fire more than once per session (clear/resume)

    if not week_file.exists():
        week_file.write_text(f"# Journal — {now.strftime('%G-W%V')}\n\n", encoding="utf-8")

    entry = f"- **{now.strftime('%Y-%m-%d %H:%M')}** · `{repo_label(data.get('cwd', ''))}` — {ask} (`{short_id}`)\n"
    with open(week_file, "a", encoding="utf-8") as f:
        f.write(entry)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never break a session over a journal line
    sys.exit(0)
