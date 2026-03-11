# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/docs` and below.
- This module owns technical documentation, architecture notes, data assumptions, testing guidance, model reports, and runbooks.

## Conventions
- Keep docs synchronized with the implementation.
- Prefer one topic per document with explicit titles.
- Record important assumptions, limitations, and metric definitions close to the feature they describe.
- Use docs to explain architecture and operational behavior, not to replace tests.

## Suggested areas
- `docs/data/`
  Data dictionary, provenance, transformation rules.
- `docs/modeling/`
  Model selection notes, evaluation summaries, limitations.
- `docs/backend/`
  API design notes, service architecture, integration behavior.
- `docs/frontend/`
  UI flows, dashboard behavior, design decisions.
- `docs/testing/`
  Test strategy, coverage expectations, QA notes.

## Do not
- Do not let docs diverge from the implemented behavior.
- Do not bury critical limitations only in chat history or commit messages.
