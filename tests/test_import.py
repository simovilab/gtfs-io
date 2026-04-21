"""Smoke tests confirming the public API surface of ``gtfs_io``."""

from __future__ import annotations

import pytest


def test_import_package() -> None:
    """The package itself should import cleanly."""
    import gtfs_io

    assert hasattr(gtfs_io, "__version__")
    assert "Feed" in gtfs_io.__all__


def test_feed_reexport() -> None:
    """``Feed`` must be importable from the top-level ``gtfs_io`` namespace."""
    from gtfs_io import Feed
    from gtfs_io.feed import Feed as FeedFromModule

    assert Feed is FeedFromModule


def test_feed_load_is_stub() -> None:
    """``Feed.load`` is a stub in the scaffold and must raise ``NotImplementedError``."""
    from gtfs_io import Feed

    with pytest.raises(NotImplementedError):
        Feed.load("gtfs.zip")


def test_feed_load_cached_is_stub() -> None:
    """``Feed.load_cached`` is a stub and must raise ``NotImplementedError``."""
    from gtfs_io import Feed

    with pytest.raises(NotImplementedError):
        Feed.load_cached()


def test_feed_instance_methods_are_stubs() -> None:
    """Instance methods are stubs and must raise ``NotImplementedError``."""
    from gtfs_io import Feed

    feed = Feed()
    with pytest.raises(NotImplementedError):
        feed.stop("ABC123")
    with pytest.raises(NotImplementedError):
        feed.validate()
