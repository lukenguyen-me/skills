# EXAMPLE: Fixture parent spec

This file is a **fixture** for dry-run / plan-mode of `develop-feature`.
It is not a real product ticket for this skills repository.

## Problem Statement

The workflow package needs a parent spec and two ordered child tickets so operators can exercise discovery without touching a product codebase.

## Solution

Keep a tiny local-markdown spec with two tracer-bullet children under `examples/issues/`.

## User Stories

1. As an operator, I want a fixture parent spec, so that plan mode has something to read.
2. As an operator, I want two ordered children, so that sequential orchestration can be described.

## Implementation Decisions

- Local markdown tracker, Matt Pocock ticket shape.
- Children numbered `01` then `02`, with `02` blocked by `01`.

## Testing Decisions

- No product tests. Verification for a real run of this fixture is out of scope.

## Out of Scope

Implementing this fixture as a real feature.

## Further Notes

Pass `{"ticket":"workflows/develop-feature/examples/parent-spec.md","mode":"plan"}`.
