"""Feed class: the primary entry point for loading and querying GTFS feeds."""

from __future__ import annotations

import csv
import hashlib
import io
import shutil
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

_PRIMARY_KEY_BY_TABLE: dict[str, str] = {
    "agency": "agency_id",
    "stops": "stop_id",
    "routes": "route_id",
    "trips": "trip_id",
    "calendar": "service_id",
    "calendar_dates": "service_id",
    "shapes": "shape_id",
    "fare_attributes": "fare_id",
}

_REQUIRED_TABLES: tuple[str, ...] = (
    "agency",
    "stops",
    "routes",
    "trips",
    "stop_times",
)

_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "stops": ("stop_id", "stop_name", "stop_lat", "stop_lon"),
    "routes": ("route_id",),
    "trips": ("route_id", "service_id", "trip_id"),
    "stop_times": ("trip_id", "stop_id", "stop_sequence"),
}

_FK_CHECKS: tuple[tuple[str, str, str, str], ...] = (
    ("trips", "route_id", "routes", "route_id"),
    ("stop_times", "trip_id", "trips", "trip_id"),
    ("stop_times", "stop_id", "stops", "stop_id"),
)


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def _read_csv_from_text(text: io.TextIOBase) -> list[dict[str, str]]:
    reader = csv.DictReader(text)
    if reader.fieldnames is None:
        return []

    rows: list[dict[str, str]] = []
    for row in reader:
        normalized = {
            key: (value if value is not None else "")
            for key, value in row.items()
            if key is not None
        }
        rows.append(normalized)
    return rows


def _read_csv_from_bytes(raw_bytes: bytes) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            decoded = raw_bytes.decode(encoding)
            return _read_csv_from_text(io.StringIO(decoded))
        except UnicodeDecodeError:
            continue

    decoded = raw_bytes.decode("latin-1", errors="replace")
    return _read_csv_from_text(io.StringIO(decoded))


def _read_folder_tables(path: Path) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    for file_path in sorted(path.glob("*.txt")):
        table_name = file_path.stem
        tables[table_name] = _read_csv_from_bytes(file_path.read_bytes())
    return tables


def _read_zip_tables(path: Path) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    with zipfile.ZipFile(path) as archive:
        for member in sorted(archive.namelist()):
            member_path = Path(member)
            if member_path.parts and member_path.parts[0] == "__MACOSX":
                continue
            if member_path.name.startswith("._"):
                continue
            if member_path.suffix.lower() != ".txt":
                continue
            with archive.open(member) as raw:
                tables[member_path.stem] = _read_csv_from_bytes(raw.read())
    return tables


def _read_zip_tables_from_bytes(content: bytes) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for member in sorted(archive.namelist()):
            member_path = Path(member)
            if member_path.parts and member_path.parts[0] == "__MACOSX":
                continue
            if member_path.name.startswith("._"):
                continue
            if member_path.suffix.lower() != ".txt":
                continue
            with archive.open(member) as raw:
                tables[member_path.stem] = _read_csv_from_bytes(raw.read())
    return tables


def _download_url_bytes(source: str) -> bytes:
    with urlopen(source) as response:  # nosec B310 - supported user-facing URL loader
        return response.read()


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
        self._source: str | None = None
        self._tables: dict[str, list[dict[str, str]]] = {}
        self._index_by_table: dict[str, dict[str, int]] = {}

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
        feed = cls()
        feed._source = source
        feed._tables = feed._load_tables(source)
        feed._index_by_table = feed._build_indexes(feed._tables)
        return feed

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
        cache_dir = Path.home() / ".cache" / "gtfs-io"
        cache_dir.mkdir(parents=True, exist_ok=True)

        if source is None:
            cached_archives = sorted(
                cache_dir.glob("*.zip"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if not cached_archives:
                raise FileNotFoundError(
                    "No cached GTFS archive found. Pass source to bootstrap cache."
                )
            return cls.load(str(cached_archives[0]))

        source_key = hashlib.sha256(source.encode("utf-8")).hexdigest()
        cached_path = cache_dir / f"{source_key}.zip"

        if cached_path.exists():
            return cls.load(str(cached_path))

        source_path = Path(source)
        if _is_url(source):
            cached_path.write_bytes(_download_url_bytes(source))
            return cls.load(str(cached_path))

        if source_path.is_file() and zipfile.is_zipfile(source_path):
            shutil.copyfile(source_path, cached_path)
            return cls.load(str(cached_path))

        return cls.load(source)

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
        stops = self._tables.get("stops", [])
        stop_index = self._index_by_table.get("stops", {})

        idx = stop_index.get(stop_id)
        if idx is None:
            raise KeyError(f"Stop {stop_id!r} was not found in this feed.")
        return stops[idx]

    def validate(self) -> list:
        """Validate the feed and return a list of validation issues.

        Returns
        -------
        list
            A list of validation issues. An empty list indicates a valid feed.
        """
        issues: list[dict[str, str]] = []

        for table_name in _REQUIRED_TABLES:
            if table_name not in self._tables:
                issues.append(
                    {
                        "kind": "missing_table",
                        "table": table_name,
                        "message": f"Missing required GTFS table: {table_name}.txt",
                    }
                )

        for table_name, required_columns in _REQUIRED_COLUMNS.items():
            rows = self._tables.get(table_name, [])
            if not rows:
                continue
            columns = set(rows[0].keys())
            for column in required_columns:
                if column not in columns:
                    issues.append(
                        {
                            "kind": "missing_column",
                            "table": table_name,
                            "column": column,
                            "message": f"Missing required column {column!r} in {table_name}.txt",
                        }
                    )

        for table_name, pk_name in _PRIMARY_KEY_BY_TABLE.items():
            rows = self._tables.get(table_name, [])
            if not rows or pk_name not in rows[0]:
                continue

            seen: dict[str, int] = {}
            for row_number, row in enumerate(rows, start=2):
                key = row.get(pk_name, "")
                if not key:
                    continue
                if key in seen:
                    issues.append(
                        {
                            "kind": "duplicate_primary_key",
                            "table": table_name,
                            "column": pk_name,
                            "key": key,
                            "message": (
                                f"Duplicate primary key {key!r} in {table_name}.txt "
                                f"(rows {seen[key]} and {row_number})."
                            ),
                        }
                    )
                else:
                    seen[key] = row_number

        for from_table, from_column, to_table, to_column in _FK_CHECKS:
            source_rows = self._tables.get(from_table, [])
            target_rows = self._tables.get(to_table, [])
            if not source_rows or not target_rows:
                continue
            if from_column not in source_rows[0] or to_column not in target_rows[0]:
                continue

            target_values = {
                row[to_column] for row in target_rows if row.get(to_column, "")
            }
            for row_number, row in enumerate(source_rows, start=2):
                value = row.get(from_column, "")
                if not value or value in target_values:
                    continue
                issues.append(
                    {
                        "kind": "missing_foreign_key",
                        "table": from_table,
                        "column": from_column,
                        "value": value,
                        "message": (
                            f"Foreign key {from_table}.{from_column}={value!r} does not resolve "
                            f"to {to_table}.{to_column} (row {row_number})."
                        ),
                    }
                )

        return issues

    @staticmethod
    def _build_indexes(
        tables: dict[str, list[dict[str, str]]],
    ) -> dict[str, dict[str, int]]:
        indexes: dict[str, dict[str, int]] = {}
        for table_name, pk_name in _PRIMARY_KEY_BY_TABLE.items():
            rows = tables.get(table_name, [])
            if not rows:
                continue
            if pk_name not in rows[0]:
                continue

            index: dict[str, int] = {}
            for idx, row in enumerate(rows):
                key = row.get(pk_name, "")
                if key and key not in index:
                    index[key] = idx
            indexes[table_name] = index
        return indexes

    @staticmethod
    def _load_tables(source: str) -> dict[str, list[dict[str, str]]]:
        source_path = Path(source)

        if source_path.is_dir():
            return _read_folder_tables(source_path)

        if source_path.is_file() and zipfile.is_zipfile(source_path):
            return _read_zip_tables(source_path)

        if _is_url(source):
            return _read_zip_tables_from_bytes(_download_url_bytes(source))

        raise FileNotFoundError(f"Unsupported GTFS source: {source!r}")
