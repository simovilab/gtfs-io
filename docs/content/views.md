---
icon: lucide/layers
---

# Views

Derived, query-friendly views over a loaded [`Feed`](feed.md).

!!! warning "Not implemented yet"
    Views are a planned part of the API. They will provide ergonomic, cached lookups (e.g., "all trips for a stop", "headways by route and service window") without requiring callers to join the raw GTFS tables themselves.

## Planned views

- Stop: upcoming arrivals
- Route: list of trips / stop patterns
- Service: active dates
- Trip: ordered stop sequence with shape geometry
