# Data Center Contract

## Zones

```text
raw/<project>/<discipline>/<document>/<revision>/
normalized/<project>/
indexes/<project>/
reports/<project>/
```

## Raw
Immutable source bytes plus identity metadata. Never rewritten by normalization or agent logic.

Required identity:
- document ID;
- discipline;
- revision;
- source location;
- SHA-256;
- baseline status.

## Normalized
Derived structured facts linked back to raw evidence.

## Indexes
Search/traceability artifacts. Index contents are derived and must never become a substitute for source evidence.

## Reports
Human-consumable generated outputs. Reports are derived artifacts and cannot redefine the baseline.
