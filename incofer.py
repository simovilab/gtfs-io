"""Manual diagnostic script for the INCOFER GTFS test feed.

Run with:
        uv run python incofer.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.gtfs_io import Feed


GTFS_PATH = Path("tests/incofer.zip")
PREVIEW_ROWS = 3
PRIORITY_TABLES = (
    "agency",
    "stops",
    "routes",
    "trips",
    "stop_times",
    "calendar",
    "calendar_dates",
)


def _format_value(value: str, max_len: int = 42) -> str:
    if len(value) <= max_len:
        return value
    return f"{value[: max_len - 3]}..."


def _print_table_preview(
    table_name: str, rows: list[dict[str, str]], *, limit: int
) -> None:
    print()
    print(f"== {table_name}.txt ==")
    print(f"Rows: {len(rows)}")

    if not rows:
        print("(empty table)")
        return

    columns = list(rows[0].keys())
    print("Columns:", ", ".join(columns))

    print(f"Preview (first {min(limit, len(rows))} rows):")
    for row in rows[:limit]:
        preview = ", ".join(
            f"{col}={_format_value(row.get(col, ''))}" for col in columns[:8]
        )
        print(f"  - {preview}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load and inspect the INCOFER GTFS archive.",
    )
    parser.add_argument(
        "--source",
        default=str(GTFS_PATH),
        help="Path to GTFS zip/folder (default: tests/incofer.zip)",
    )
    parser.add_argument(
        "--preview-rows",
        type=int,
        default=PREVIEW_ROWS,
        help="Number of rows to preview per table.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run Feed.validate() and print a short issue summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    source_path = Path(args.source)

    print("Loading GTFS feed...")
    print(f"Source: {source_path}")

    if not source_path.exists():
        raise FileNotFoundError(f"GTFS archive not found: {source_path}")

    feed = Feed.load(str(source_path))
    tables = feed._tables

    print()
    print("Load status: OK")
    print(f"Tables loaded: {len(tables)}")
    print(
        "Hidden metadata tables present:",
        any(name.startswith("._") or name.startswith("__MACOSX") for name in tables),
    )

    print()
    print("Table inventory (sorted):")
    for table_name in sorted(tables):
        print(f"  - {table_name}.txt: {len(tables[table_name])} rows")

    print()
    print("Detailed previews for key tables:")
    for table_name in PRIORITY_TABLES:
        if table_name in tables:
            _print_table_preview(
                table_name, tables[table_name], limit=args.preview_rows
            )

    if "stops" in tables and tables["stops"]:
        sample_stop_id = tables["stops"][0].get("stop_id")
        if sample_stop_id:
            stop = feed.stop(sample_stop_id)
            print()
            print("Sample stop lookup using Feed.stop:")
            print(f"  stop_id={sample_stop_id}, stop_name={stop.get('stop_name', '')}")

    if args.validate:
        issues = feed.validate()
        print()
        print(f"Validation issues found: {len(issues)}")
        for issue in issues[:10]:
            print(f"  - [{issue.get('kind', 'unknown')}] {issue.get('message', '')}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")


if __name__ == "__main__":
    main()
