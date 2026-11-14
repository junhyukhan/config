# Claude settings: public defaults, private runtime file

`claude/.claude/settings.json` is a **public bootstrap template**, not a live
Stow target. It contains generic guard policy, permission rules, hook registration
and ordinary defaults. Concrete hostnames, network addresses and private
repository inventories belong only in the machine's regular
`~/.claude/settings.json` file. Do not store credentials in either file.

## Install and migration

`python3 scripts/install-claude-settings.py`:

- Creates a mode-0600 local file on a fresh machine from the public template.
- Replaces a legacy symlink to this repository's template with a mode-0600 regular
  file, preserving its exact contents. No values are printed.
- Validates but never overwrites an existing regular local settings file.
- Refuses unfamiliar symlinks, folded settings directories and invalid JSON.

The `claude/.stow-local-ignore` rule prevents Stow from linking settings again.
Hooks remain linked with `--no-folding`. `setup.sh` runs the helper before Stow;
it does not invoke Claude or need a service restart for this migration.

**On another existing machine, preserve local settings before updating the
checkout.** A pull changes the contents of an old settings symlink immediately.
Before pulling, detach that link while preserving its contents, for example:

```bash
if test -L "$HOME/.claude/settings.json"; then
    (umask 077
     test ! -e "$HOME/.claude/settings.json.local-copy" &&
     test ! -L "$HOME/.claude/settings.json.local-copy" &&
     cp -L "$HOME/.claude/settings.json" "$HOME/.claude/settings.json.local-copy" &&
     mv "$HOME/.claude/settings.json.local-copy" "$HOME/.claude/settings.json")
fi
```

Review file conflicts first; do not overwrite an existing `.local-copy` backup.
If the checkout was already updated before detaching, the old machine inventory
may no longer be present in the linked file. Restore it from an authorized private
source, not from guessed values or agent session histories.

## Updating

Application-written preferences and personal guard context now stay local.
Pulling public defaults **does not update existing local settings**. Review and
apply intended template changes deliberately, retaining local guard context and
preferences. Hook source edits still become live through their Stow links.

A bootstrap test proves file handling, not that a model makes equivalent approval
decisions. Preserve the existing runtime settings exactly when migrating; do not
weaken permissions or the private trust inventory merely to sanitize git.

## Offline verification

```bash
python3 -B -m unittest discover -s scripts -p 'test_install_claude_settings.py' -v
python3 -B claude/.claude/hooks/guard-secret-env.test.py
stow -n -R --no-folding -t "$HOME" claude
```

Installer tests use synthetic homes and settings, including a real Stow/restow
check when GNU Stow is available. Hook tests feed synthetic command strings to the
guard; those commands are not executed and no secret files are opened.

## Decision

> **Verbatim (Han, 2026-11-15):** "a but can you make the changes?"

"a" was finishing and landing this split, which an agent drafted on 2026-11-09 and left uncommitted.
The alternatives were discarding it or leaving it. The full personal records it trims are kept in a
private archive.
