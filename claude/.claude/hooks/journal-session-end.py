#!/usr/bin/env python3
"""SessionEnd hook: append a one-line stub for this session to the work journal,
then commit just that line (local, pathspec-scoped, no push).

Journal layout: ~/workdir/repos/journal/YYYY/YYYY-Www.md (ISO week, one file per
week, append-only). Each line is a pure time-marker: timestamp, repo, session id.
Prompt text is deliberately NOT recorded — the first user prompt is usually
orientation/bookkeeping ("do I have unpushed repos"), so capturing it masqueraded as
a summary without being one; substance lives in hand-written layer-2 lines. Zero agent
tokens — this runs as a plain script after the session ends.

Committing here keeps the working tree clean after every session; pushing stays
off the lifecycle (on-demand via /sync-repos) so nothing in this hook can hang on
the network. The commit is safe at SessionEnd — the "don't auto-commit" concern was
index contention with a *live* session, which is gone once the session has ended.

Fail-silent by design: a journal miss must never break a session. The transcript
is read only to check that a real user prompt exists (the trivial-session gate); no
transcript content is recorded.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

JOURNAL_ROOT = Path.home() / "workdir" / "repos" / "journal"
REPOS_ROOT = Path.home() / "workdir" / "repos"


def has_real_user_prompt(transcript_path):
    """True if the transcript holds at least one real (typed) user message.

    Used only as a gate: a session with no typed prompt is trivial and gets no journal
    line. The message text itself is not recorded — the stub is a pure time-marker.
    """
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
                return True
    except OSError:
        pass
    return False


def repo_label(cwd):
    """First path component under ~/workdir/repos, or the cwd basename."""
    try:
        rel = Path(cwd).resolve().relative_to(REPOS_ROOT)
    except ValueError:
        return Path(cwd).name or "?"
    return rel.parts[0] if rel.parts else "repos"


def commit_stub(repo_root, week_file):
    """Commit just this journal line — pathspec-scoped, local, never pushes.

    The explicit `-- <path>` on both add and commit means only the journal file is
    ever touched; unrelated staged/working changes in the meta-repo are left alone.
    A concurrent SessionEnd in another repo can lose the git index.lock race; that
    just leaves the line uncommitted for the next sweep to pick up (same as before).
    """
    rel = str(week_file.relative_to(repo_root))
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=10, env=env,
        )

    git("add", "--", rel)
    git("commit", "-m", f"journal: session stub ({week_file.stem})", "--", rel)


def main():
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "")
    if not has_real_user_prompt(data.get("transcript_path", "")):  # trivial session, skip
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

    entry = f"- **{now.strftime('%Y-%m-%d %H:%M')}** · `{repo_label(data.get('cwd', ''))}` · `{short_id}`\n"
    with open(week_file, "a", encoding="utf-8") as f:
        f.write(entry)

    commit_stub(JOURNAL_ROOT.parent, week_file)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never break a session over a journal line
    sys.exit(0)
