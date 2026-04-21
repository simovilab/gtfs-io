---
icon: lucide/rocket
---

# Get Started

**gtfs-io** is a Python library for reading, writing, and validating [GTFS](https://gtfs.org/) (General Transit Feed Specification) data.

!!! warning "Pre-alpha"
    The public API is being sketched; most methods are currently stubs that raise `NotImplementedError`. Expect breaking changes.

## Installation

=== ":simple-uv: uv"

    ```bash
    uv add gtfs-io
    ```

=== ":simple-pypi: pip"

    ```bash
    pip install gtfs-io
    ```

## Quick example

```python
from gtfs_io import Feed

feed = Feed.load("gtfs.zip")
stop = feed.stop("ABC123")
issues = feed.validate()
```

## Where to next?

- [I/O](io.md) — read and write GTFS archives.
- [Models](models.md) — typed data classes for GTFS entities.
- [Validation](validate.md) — check a feed for spec compliance.
- [Views](views.md) — derived, query-friendly views over a feed.
- [Feed](feed.md) — the top-level [`Feed`][gtfs_io.Feed] entry point.
