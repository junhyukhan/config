# Setting up a new Mac

This public guide covers generic bootstrap steps. Keep actual repository
inventories, host mappings, machine roles and migration checklists private. The
original personalized guide has been retained in a private historical archive;
its old machine state is not a current setup instruction.

## Bootstrap

1. Install the Xcode command-line tools and Homebrew using their official guides.
2. Clone this public configuration repository and review `setup.sh` before running
   it. Setup installs packages, changes the default shell, links configs, and may
   install tool integrations; it is not a links-only command.
3. Review conflicts before replacing existing files. Stow must not silently adopt
   an application's existing local configuration.
4. Install any required tools not in the Brewfile using their recommended source,
   then sign in interactively. Do not copy credentials into this repository.
5. Bootstrap Claude settings with `python3 scripts/install-claude-settings.py`.
   `~/.claude/settings.json` is a private regular file; review and supply actual
   machine-specific guard context there. It is not symlinked back into git.
6. Restore authorized local configuration through a private migration procedure.
   Actual SSH aliases, repository URLs and service addresses do not belong here.

## Rules

- The Brewfile is the shared core. Additional device-specific apps can remain
  manually installed.
- Never run `brew bundle cleanup` against the core-only Brewfile.
- Applications that update themselves need not be reinstalled just to adopt them
  into a package manager. Review version compatibility before any adoption.
- Configure macOS preferences by hand; they are not tracked here.
- Do not put credentials, environment-secret files or agent session state in git.

See [`claude-settings.md`](claude-settings.md) for the local-settings boundary and
safe migration order on an existing machine.
