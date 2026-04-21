---
icon: lucide/import
---

# I/O

Low-level helpers for reading and writing GTFS archives and text files.

!!! warning "Not implemented yet"
    This module currently only defines the package boundary. Readers and writers for GTFS zip archives and on-disk folders are planned.

## Planned surface

- `gtfs_io.io.read_zip(path_or_url)` — load a GTFS zip archive.
- `gtfs_io.io.read_folder(path)` — load a folder of GTFS `.txt` files.
- `gtfs_io.io.write_zip(feed, path)` — serialize a feed to a zip archive.
