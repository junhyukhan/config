# New-Mac setup — public summary

The original personal setup decisions and machine-role discussion have been
retained verbatim in a private archive. The public runbook is
[`../new-mac.md`](../new-mac.md).

The Brewfile describes the shared core, not every app on every device. Do not run
`brew bundle cleanup` against a core-only list: it can remove intentionally
installed extras. Prefer a vendor's recommended installer when appropriate.

Actual repository inventories, SSH mappings, machine roles and migration details
belong in private records or machine-local configuration, not this public guide.
