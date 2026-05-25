"""Smoke tests confirming the public API surface of ``gtfs_io``."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


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


def _write_minimal_feed(folder: Path) -> None:
    (folder / "agency.txt").write_text(
        dedent(
            """\
            agency_id,agency_name,agency_url,agency_timezone
            AGENCY,Transit Agency,https://example.com,America/Santiago
            """
        ),
        encoding="utf-8",
    )
    (folder / "stops.txt").write_text(
        dedent(
            """\
            stop_id,stop_name,stop_lat,stop_lon
            ABC123,Main St,10.000,-84.000
            XYZ999,Central,10.100,-84.100
            """
        ),
        encoding="utf-8",
    )
    (folder / "routes.txt").write_text(
        dedent(
            """\
            route_id,route_short_name,route_long_name,route_type
            R1,1,Route 1,3
            """
        ),
        encoding="utf-8",
    )
    (folder / "trips.txt").write_text(
        dedent(
            """\
            route_id,service_id,trip_id
            R1,WKD,T1
            """
        ),
        encoding="utf-8",
    )
    (folder / "stop_times.txt").write_text(
        dedent(
            """\
            trip_id,arrival_time,departure_time,stop_id,stop_sequence
            T1,08:00:00,08:00:00,ABC123,1
            T1,08:05:00,08:05:00,XYZ999,2
            """
        ),
        encoding="utf-8",
    )


def test_feed_load_from_folder_and_stop_lookup(tmp_path: Path) -> None:
    """``Feed.load`` should parse folder feeds and support indexed stop lookups."""
    from gtfs_io import Feed

    _write_minimal_feed(tmp_path)
    feed = Feed.load(str(tmp_path))

    stop = feed.stop("ABC123")
    assert stop["stop_name"] == "Main St"
    assert stop["stop_lat"] == "10.000"


def test_feed_validate_minimal_feed_has_no_issues(tmp_path: Path) -> None:
    """A minimal valid fixture should produce no baseline validation issues."""
    from gtfs_io import Feed

    _write_minimal_feed(tmp_path)
    feed = Feed.load(str(tmp_path))

    assert feed.validate() == []


def test_feed_validate_reports_missing_tables(tmp_path: Path) -> None:
    """Validation should report missing required tables."""
    from gtfs_io import Feed

    (tmp_path / "stops.txt").write_text(
        "stop_id,stop_name,stop_lat,stop_lon\nS1,Only Stop,0,0\n",
        encoding="utf-8",
    )
    feed = Feed.load(str(tmp_path))
    issues = feed.validate()

    issue_kinds = {issue["kind"] for issue in issues}
    assert "missing_table" in issue_kinds


def test_feed_load_non_utf8_zip(tmp_path: Path) -> None:
    """Feed loading should tolerate common legacy encodings in GTFS text files."""
    from gtfs_io import Feed

    zip_path = tmp_path / "legacy.zip"
    with zipfile.ZipFile(zip_path, mode="w") as archive:
        archive.writestr(
            "agency.txt",
            "agency_id,agency_name,agency_url,agency_timezone\nA1,Agencia,http://x,America/Costa_Rica\n",
        )
        archive.writestr(
            "stops.txt",
            "stop_id,stop_name,stop_lat,stop_lon\nS1,Parada Acera Norte,9.93,-84.08\n".encode(
                "cp1252"
            ),
        )
        archive.writestr(
            "routes.txt",
            "route_id,route_short_name,route_long_name,route_type\nR1,1,Ruta 1,3\n",
        )
        archive.writestr(
            "trips.txt",
            "route_id,service_id,trip_id\nR1,WKD,T1\n",
        )
        archive.writestr(
            "stop_times.txt",
            "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
            "T1,08:00:00,08:00:00,S1,1\n",
        )

    feed = Feed.load(str(zip_path))
    stop = feed.stop("S1")

    assert stop["stop_name"] == "Parada Acera Norte"
