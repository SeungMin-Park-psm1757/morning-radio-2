# Decision Log

## D-001
Build weekly quantum as a separate additive namespace.
Reason:
- lower regression risk for the current daily pipeline.

## D-002
Use direct site collectors instead of Google News query collection.
Reason:
- user wants approved-source-only coverage.

## D-003
Use global dedup before LLM expansion.
Reason:
- prevents token waste and duplicate story narration.

## D-004
Use representative-only detail enrichment.
Reason:
- cheapest reliable summary pipeline.

## D-005
Ship two audio products.
Reason:
- one full show for listeners, one quick headlines track for time-constrained users.

## D-006
Persist last successful run state.
Reason:
- missed schedules should not create blind spots.

## D-007
Treat GitHub Actions as MVP scheduling, not perfect timing infrastructure.
Reason:
- schedule drift and inactivity constraints exist.
