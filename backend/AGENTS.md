# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/Analytic_capstone_proj/backend` and below.
- This module owns APIs, application services, domain workflows, orchestration, persistence integration, and model-serving endpoints.
- Primary stack: Python + FastAPI.
- Current status: this module is not bootstrapped yet. Create the backend structure under this directory instead of placing API code at repository root.

## Expected layout
- `src/`
  Main backend source code.
- `src/api/`
  Request handlers, controllers, transport schemas, and response mapping.
- `src/services/`
  Application services and use-case orchestration.
- `src/domain/`
  Core business rules and pricing logic.
- `src/repositories/`
  Persistence access and storage adapters.
- `src/config/`
  Runtime configuration and dependency wiring.
- `tests/`
  Backend unit and integration tests.

## Commands
- Bootstrap Python tooling inside `backend/` before adding runtime-specific instructions.
- Expected backend entrypoint after bootstrap: a FastAPI application under `src/`.
- Preferred test framework: `pytest`.

## Conventions
- Keep controllers thin. Put business logic in services or domain modules.
- Name files by responsibility, for example `market_benchmark_controller`, `listing_similarity_service`, `price_estimation_use_case`.
- Keep request/response transport models separate from domain models.
- Validate inputs at the boundary and return explicit errors.
- Avoid cross-importing unrelated feature areas.

## Testing
- Every endpoint needs integration coverage.
- Every service or domain rule needs unit coverage.
- New backend features must include both success-path and failure-path tests where relevant.
- Keep backend coverage at or above `85%`.

## Do not
- Do not place pricing logic directly in controllers.
- Do not hide business rules inside ORM models or persistence adapters.
- Do not merge new behavior without tests.
