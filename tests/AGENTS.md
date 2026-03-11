# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/tests` and below.
- This module owns cross-module integration tests, end-to-end tests, fixtures, and test harnesses that do not belong to a single module.
- Expected scope: backend/frontend integration and end-to-end validation across the FastAPI and Next.js stack.

## Expected layout
- `integration/`
  Multi-module interaction tests.
- `e2e/`
  End-to-end workflow tests.
- `fixtures/`
  Shared test datasets and sample payloads.
- `helpers/`
  Shared test utilities only when reuse is real.

## Conventions
- Name tests by behavior, for example `benchmark_generation_integration_test` and `price_positioning_dashboard_e2e_test`.
- Keep fixtures readable and intentionally small unless large-volume behavior is under test.
- Prefer realistic data shapes over heavily mocked synthetic structures.

## Testing
- Cover critical workflows end to end once the product surface exists.
- Add integration coverage for backend and frontend boundaries.
- Use this module to protect against cross-module regressions.

## Do not
- Do not duplicate unit tests that already belong in owning modules.
- Do not store unexplained fixture files.
