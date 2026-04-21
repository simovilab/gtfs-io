"""Feed class: the primary entry point for loading and querying GTFS feeds."""

from __future__ import annotations

from typing import Any


class Feed:
    """An in-memory representation of a GTFS feed.

    A :class:`Feed` is typically constructed via one of its classmethods:

    - :meth:`Feed.load` to load from a local file path or URL.
    - :meth:`Feed.load_cached` to load from a local cache, optionally
      falling back to ``source``.

    Example
    -------
    >>> from gtfs_io import Feed
    >>> feed = Feed.load("gtfs.zip")          # doctest: +SKIP
    >>> stop = feed.stop("ABC123")            # doctest: +SKIP
    """

    def __init__(self) -> None:
        """Construct an empty :class:`Feed`.

        End users are expected to use :meth:`load` or :meth:`load_cached`
        rather than calling this constructor directly.
        """

    # ------------------------------------------------------------------ #
    # Constructors
    # ------------------------------------------------------------------ #
    @classmethod
    def load(cls, source: str) -> "Feed":
        """Load a GTFS feed from a local file path or URL.

        Parameters
        ----------
        source:
            A filesystem path or URL pointing to a GTFS zip archive or
            a directory of GTFS text files.

        Returns
        -------
        Feed
            A fully-loaded feed.
        """
        raise NotImplementedError

    @classmethod
    def load_cached(cls, source: str | None = None) -> "Feed":
        """Load a GTFS feed from the local cache.

        Parameters
        ----------
        source:
            Optional source identifier used both as a cache key and as a
            fallback to fetch from if the cache is empty.

        Returns
        -------
        Feed
            A fully-loaded feed.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Instance API
    # ------------------------------------------------------------------ #
    def stop(self, stop_id: str) -> Any:
        """Return the stop identified by ``stop_id``.

        Parameters
        ----------
        stop_id:
            The GTFS ``stop_id`` to look up.
        """
        raise NotImplementedError

    def validate(self) -> list:
        """Validate the feed and return a list of validation issues.

        Returns
        -------
        list
            A list of validation issues. An empty list indicates a valid feed.
        """
        raise NotImplementedError
