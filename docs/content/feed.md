---
icon: lucide/database
---

# Feed

The [`Feed`][gtfs_io.Feed] class is the single entry point for working with a GTFS dataset.

!!! warning "Stubbed API"
    All methods currently raise `NotImplementedError`. The signatures below describe the intended public API.

## Constructors

### `Feed.load(source)`

Load a GTFS feed from a local file path or URL.

```python
from gtfs_io import Feed

feed = Feed.load("gtfs.zip")
feed = Feed.load("https://example.com/gtfs.zip")
```

### `Feed.load_cached(source=None)`

Load a GTFS feed from the local cache. If `source` is provided it is used as both the cache key and as a fallback to fetch from when the cache is empty.

```python
feed = Feed.load_cached("https://example.com/gtfs.zip")
```

## Instance methods

### `feed.stop(stop_id)`

Return the stop identified by `stop_id`.

### `feed.validate()`

Validate the feed and return a list of issues. An empty list indicates a valid feed. See [Validation](validate.md) for details on planned checks.
