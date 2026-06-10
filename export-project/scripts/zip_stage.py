#!/usr/bin/env python3
"""
zip_stage.py — Zips the staging directory into a final export archive.

Usage:
    python zip_stage.py [--staging-dir /path] [--output /path/to/export.zip]
"""

import argparse
import sys
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Zip the staged export directory.")
    parser.add_argument("--staging-dir", default="/tmp/project-export-stage")
    parser.add_argument("--output", default="/mnt/user-data/outputs/project-export.zip")
    args = parser.parse_args()

    stage = Path(args.staging_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not stage.exists():
        print(f"ERROR: staging dir not found: {stage}", file=sys.stderr)
        return 1

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(stage))

    file_count = sum(1 for _ in stage.rglob("*") if _.is_file())
    size_kb = out.stat().st_size / 1024
    print(f"Zipped {file_count} file(s) → {out}  ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
