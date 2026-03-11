# Agent instructions (scope: this directory and subdirectories)

## Scope and ownership
- This AGENTS.md applies to `/home/arch/Scrivania/archive/shared` and below.
- This module owns shared schemas, validation rules, constants, typed contracts, and utilities used by multiple modules.
- Primary role: language-agnostic contracts and shared validation artifacts between backend, modeling, and frontend.

## Expected layout
- `src/schemas/`
  Shared request, response, and data contracts.
- `src/types/`
  Cross-module types.
- `src/validation/`
  Shared validation logic.
- `src/constants/`
  Stable constants and enumerations.
- `tests/`
  Shared unit tests.

## Conventions
- Keep shared code small and intentional.
- Only place code here when it is truly used by multiple modules.
- Prefer stable names such as `listing_schema`, `market_segment_type`, and `price_range_validator`.
- Preserve backward compatibility carefully once other modules depend on these contracts.

## Testing
- Every shared contract or validator requires direct unit tests.
- Keep shared coverage at or above `85%`.

## Do not
- Do not turn `shared/` into a dumping ground.
- Do not add feature-specific business logic here.
