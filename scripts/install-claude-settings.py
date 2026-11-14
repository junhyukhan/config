#!/usr/bin/env python3
"""Bootstrap local Claude settings; never symlink personal guard context into git.

Only the legacy symlink to this repository's settings template is migrated.
Existing regular settings are validated and left byte-for-byte unchanged.
No settings values are logged. This does not invoke Claude or install tools.
"""
import json
import os
from pathlib import Path
import sys
import tempfile


class SettingsError(Exception):
    pass


def validate(payload):
    try:
        settings = json.loads(payload)
    except (ValueError, UnicodeError):
        raise SettingsError("settings must be valid JSON") from None
    if not isinstance(settings, dict):
        raise SettingsError("settings must be a JSON object")
    return settings


def install(repo, home):
    source = repo / "claude/.claude/settings.json"
    directory = home / ".claude"
    target = directory / "settings.json"
    if directory.is_symlink():
        raise SettingsError("refusing a symlinked settings directory; migrate it manually")
    if target.is_symlink():
        if target.resolve() != source.resolve():
            raise SettingsError("refusing an unfamiliar settings symlink")
        payload = source.read_bytes()
        action = "migrated legacy settings symlink to a private regular file"
    elif target.exists():
        if not target.is_file():
            raise SettingsError("settings target is not a regular file")
        validate(target.read_bytes())
        return "preserved existing local settings (no changes)"
    else:
        payload = source.read_bytes()
        action = "created local settings from generic defaults; review local guard context"
    validate(payload)
    directory.mkdir(parents=True, exist_ok=True)
    # Replace the link, never write through it. mkstemp creates mode 0600.
    fd, name = tempfile.mkstemp(prefix=".settings-", dir=directory)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return action


def main():
    if len(sys.argv) != 1:
        print("Usage: python3 scripts/install-claude-settings.py", file=sys.stderr)
        return 2
    try:
        print(install(Path(__file__).resolve().parent.parent, Path.home()))
    except (OSError, SettingsError):
        # Do not print exception text: malformed JSON or paths may be private.
        print("Claude settings were not installed: check JSON, permissions and symlink ownership; no values logged.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
