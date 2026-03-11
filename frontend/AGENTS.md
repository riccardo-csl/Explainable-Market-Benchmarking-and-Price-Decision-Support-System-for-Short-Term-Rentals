# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/frontend` and below.
- This module owns the dashboard UI, user interactions, charts, forms, and presentation logic.
- Primary stack: Next.js + React.

## Expected layout
- `src/`
  Main frontend source code.
- `src/pages/` or `src/routes/`
  Route-level entrypoints.
- `src/features/`
  Feature-oriented UI modules.
- `src/components/`
  Shared presentational components.
- `src/lib/`
  UI-safe helpers, formatting, and client-side adapters.
- `tests/`
  Component, integration, and UI workflow tests.

## Commands
- Use standard Next.js project commands once initialized.
- Preferred test frameworks: unit and component tests for UI logic, with integration coverage for feature flows.

## Conventions
- Group UI code by feature instead of creating large global folders of unrelated files.
- Keep data fetching and view composition separate from purely presentational components.
- Use descriptive filenames such as `price_positioning_panel`, `benchmark_range_card`, and `comparable_listings_table`.
- Prefer reusable components only when they are genuinely shared.
- Keep charts and derived presentation logic easy to test.

## Testing
- Every new user-facing feature requires component or integration coverage.
- Critical workflows need end-to-end coverage through the top-level `tests/` module once available.
- Keep frontend coverage at or above `85%`.

## Do not
- Do not place business logic in view components.
- Do not create generic files such as `helpers.tsx` when the file has a clear domain responsibility.
- Do not add untested UI states.
