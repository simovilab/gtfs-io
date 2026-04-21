# gtfs-io

A Python library for reading, writing, and validating GTFS (General Transit
Feed Specification) data.

> Status: **pre-alpha**. The public API is being sketched; most methods are
> currently stubs that raise `NotImplementedError`.

## Installation

```bash
pip install gtfs-io
```

or, with [uv](https://docs.astral.sh/uv/):

```bash
uv add gtfs-io
```

## Example

```python
from gtfs_io import Feed

feed = Feed.load("gtfs.zip")
stop = feed.stop("ABC123")
```

You can also load from a cached copy:

```python
from gtfs_io import Feed

feed = Feed.load_cached("https://example.com/gtfs.zip")
issues = feed.validate()
```

## License

MIT — see [`LICENSE`](./LICENSE).
