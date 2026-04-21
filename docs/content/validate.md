---
icon: lucide/list-checks
---

# Validation

Checks that verify a GTFS feed conforms to the specification.

!!! warning "Not implemented yet"
    The validation engine is not implemented. [`Feed.validate`](validate.md) is a stub that will eventually return a list of issues found in the feed.

## Planned checks

- Required files and columns are present.
- Primary and foreign key integrity (e.g., every `stop_times.stop_id` resolves).
- Value-level constraints (types, ranges, enumerations, time formats).
- Referential consistency across `trips`, `routes`, `shapes`, `calendar`.
