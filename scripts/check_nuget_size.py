#!/usr/bin/env python3
"""Gate the compressed .nupkg size before restore or publication.

NUGET_MAX_PACKAGE_BYTES is a positive integer byte budget (default
249,000,000, conservatively below nuget.org's approximately 250 MB limit).
Only ZIP metadata is read; payloads are never extracted or decompressed.
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

import cpp_project as cp

DEFAULT_MAX_BYTES = 249_000_000


def check(package: Path) -> None:
    raw = os.environ.get("NUGET_MAX_PACKAGE_BYTES") or str(DEFAULT_MAX_BYTES)
    try:
        budget = int(raw)
    except ValueError:
        raise ValueError("NUGET_MAX_PACKAGE_BYTES must be a positive integer byte count") from None
    if budget <= 0:
        raise ValueError("NUGET_MAX_PACKAGE_BYTES must be a positive integer byte count")
    size = package.stat().st_size
    with zipfile.ZipFile(package) as archive:
        entries = archive.infolist()
    print(f"NuGet size: {package}: {size:,} bytes; budget {budget:,} bytes")
    if size > budget:
        print("Largest ZIP entries (compressed bytes / uncompressed bytes):", file=sys.stderr)
        for entry in sorted(entries, key=lambda e: e.compress_size, reverse=True)[:10]:
            # repr keeps untrusted filenames from emitting workflow commands.
            print(f"  {entry.compress_size:,} / {entry.file_size:,}  {entry.filename!r}", file=sys.stderr)
        raise ValueError(
            f"{package} is {size:,} bytes, exceeding the {budget:,}-byte budget. "
            "Remove unused payloads or split native platforms into separate packages before publishing."
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("package", type=Path)
    args = parser.parse_args(argv)
    try:
        check(args.package)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        cp.error(str(exc), title="NuGet package size check failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
