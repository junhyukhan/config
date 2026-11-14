# Supabase MCP — public summary

The original personal decision record, amendments and project-specific evidence
have been retained verbatim in a private archive. This summary is not new
permission to access a database or change its configuration.

General lessons:

- A server's read-only launch flag and a client's approval prompt are different
  mechanisms. Approving a call cannot make an already read-only server accept it.
- Tool-list appearance is version-dependent; verify effective configuration and
  behavior rather than treating an advertised tool as proof of write access.
- Keep project identifiers and credentials out of public configuration. Scope
  actual server definitions locally and use reviewed migration artifacts for
  authorized schema changes.
- Interactive shell startup is not equivalent to the environment inherited by a
  non-interactive child. Diagnose that boundary without printing token values.
- Secret values must never enter logs or public files; move them file-to-file
  only under explicit authorization.

This cleanup does not change MCP definitions, token handling or database access.
