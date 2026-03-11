# Agent instructions (scope: this directory and subdirectories)

## Scope and layout
- This AGENTS.md applies to `/home/arch/Scrivania/archive` and below.
- This repository currently contains datasets and project documents. Treat it as the root of a new software project and keep the codebase modular from the first implementation step.
- Prefer creating clear top-level modules instead of placing application code in the repository root.
- Approved initial stack: `backend` in Python with FastAPI, `modeling` in Python, `frontend` in Next.js/React, `shared` for shared contracts and schemas, and `tests` for cross-module integration and end-to-end coverage.

## Planned project structure
- `data/`
  Store immutable input datasets, derived datasets, and dataset metadata. Keep raw files read-only and place generated outputs in dedicated subdirectories such as `data/raw/`, `data/processed/`, and `data/external/`.
- `backend/`
  Owns APIs, business logic, model-serving endpoints, orchestration, and persistence.
- `frontend/`
  Owns dashboard UI, visualization, and user-facing workflows.
- `shared/`
  Owns shared schemas, DTOs, validation rules, constants, and utilities used across modules.
- `modeling/`
  Owns exploratory modeling code, feature engineering pipelines, training jobs, evaluation reports, and reproducible experiment code.
- `tests/`
  Owns cross-module integration tests, end-to-end tests, shared fixtures, and test utilities that do not belong to a single module.
- `docs/`
  Owns technical docs, ADRs, data dictionary, model cards, and runbooks.

## Modules / subprojects

| Module | Type | Path | What it owns | How to run | Tests | Docs | AGENTS |
|--------|------|------|--------------|------------|-------|------|--------|
| data | data | `data/` | Raw and processed datasets, metadata, data contracts | Validation-only | Data validation checks | `docs/data/` | `data/AGENTS.md` |
| modeling | python | `modeling/` | Feature engineering, training, evaluation, experiments | Python tooling | Pytest + evaluation tests | `docs/modeling/` | `modeling/AGENTS.md` |
| backend | fastapi | `backend/` | APIs, business logic, model access, persistence | FastAPI app | Pytest unit + integration tests | `docs/backend/` | `backend/AGENTS.md` |
| frontend | nextjs | `frontend/` | Dashboard, UX flows, charts, forms | Next.js app | Unit + integration tests | `docs/frontend/` | `frontend/AGENTS.md` |
| shared | schemas | `shared/` | Shared contracts, schemas, typed utilities | Module-specific | Unit tests | `docs/shared/` | `shared/AGENTS.md` |
| tests | qa | `tests/` | End-to-end coverage, fixtures, test harnesses | Module-specific | Full-system tests | `docs/testing/` | `tests/AGENTS.md` |

## Global conventions
- Use modular files and directories with clear, descriptive names that a new engineer can understand without extra context.
- Prefer names such as `price_estimation_service`, `listing_similarity_engine`, `market_benchmark_controller`, and `seasonal_benchmark_calculator` over vague names such as `utils2`, `misc`, `helpers`, or `temp`.
- Keep files focused. If a file starts owning multiple unrelated responsibilities, split it.
- Keep business rules out of controllers and UI components. Put domain logic in dedicated services or domain modules.
- Keep data access, model logic, API transport, and presentation concerns separate.
- Add concise comments only where the logic is not immediately obvious.
- Prefer explicit types, schemas, and validation at module boundaries.
- Any new functionality must be accompanied by tests in the same change.
- Minimum test coverage for the project is `85%`. New code should not reduce the effective coverage below this threshold.
- Treat missing tests for new behavior as a defect, not as optional follow-up work.

## Testing expectations
- Every new feature must include happy-path tests, edge-case tests, and failure-path tests where relevant.
- Every bug fix must include a regression test unless that is technically impossible; if impossible, explain the reason in the change summary.
- Prefer unit tests for pure logic, integration tests for module boundaries, and end-to-end tests only for critical user workflows.
- Mock only true external dependencies. Do not mock internal logic so aggressively that tests stop validating real behavior.
- Keep test data readable and intentionally named.
- If a module introduces a contract, parser, transformation, or pricing rule, test it directly.
- If a module exposes an API or UI workflow, add integration coverage for the full interaction path.

## Code organization rules
- Create one main responsibility per module and one clear entrypoint per feature area.
- Group files by feature or domain responsibility, not by generic technical labels alone.
- Use stable, understandable filenames. Good examples: `listing_price_estimator.py`, `benchmark_range_service.ts`, `micro_market_clusterer.py`, `price_positioning_badge.tsx`.
- Avoid catch-all files such as `common.py`, `helpers.ts`, `stuff.js`, or `data_new_final.py`.
- Keep configuration explicit and close to the owning module.
- Keep notebooks exploratory only. Production logic must live in normal source files that can be tested and imported.

## Data and modeling rules
- Do not modify source CSV or source document files in place.
- Any derived dataset must document its origin, transformation steps, and schema.
- Training, evaluation, and inference code must be reproducible and separated from one-off exploration.
- Record assumptions and limitations for any benchmark, estimator, or clustering logic in `docs/`.
- Do not claim occupancy, revenue, elasticity, or dynamic pricing capabilities unless the supporting data and validation actually exist.

## Verification guidance
- Run the narrowest relevant tests first, then broader suites before considering work complete.
- Nested module `AGENTS.md` files should be kept aligned with the approved stack and updated if tooling changes.
- Before merging substantial work, verify formatting, linting, type checks, and tests for every touched module.
- Coverage checks must be part of the normal verification path once the project test harness exists.

## Docs usage
- Do not open or expand `docs/` by default unless the task requires it.
- Keep architecture decisions, data assumptions, and evaluation limitations documented as the project evolves.

## Do not
- Do not place new application code in the repository root.
- Do not create ambiguous filenames or overloaded modules.
- Do not add a new feature without tests.
- Do not accept coverage below `85%` unless the user explicitly approves a temporary exception.
- Do not hide important assumptions in notebooks or ad hoc scripts.

## Next-step rule
- Keep module-level `AGENTS.md` files synchronized with the actual FastAPI, Python, Next.js, and testing setup as the project is bootstrapped.
