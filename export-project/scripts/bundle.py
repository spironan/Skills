#!/usr/bin/env python3
"""
bundle.py — Collects static project assets into a staging directory for export.

Usage:
    python bundle.py [--staging-dir /path/to/stage]

Outputs a staging directory with:
    uploads/        — 1:1 copy of /mnt/user-data/uploads/
    transcripts_raw/ — raw transcript files for Claude to compact
    meta.json       — inventory + timestamp
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

UPLOADS_SRC = Path("/mnt/user-data/uploads")
TRANSCRIPTS_SRC = Path("/mnt/transcripts")


def copy_tree_if_exists(src: Path, dst: Path) -> list[str]:
    """Copy src to dst recursively. Returns list of relative paths copied."""
    collected = []
    if not src.exists():
        return collected
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            collected.append(str(rel))
    return collected


def main():
    parser = argparse.ArgumentParser(description="Stage project assets for export.")
    parser.add_argument(
        "--staging-dir",
        default="/tmp/project-export-stage",
        help="Directory to stage files in (will be created/overwritten)",
    )
    args = parser.parse_args()

    stage = Path(args.staging_dir)
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    meta = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "sources": {},
    }

    # 1. Uploads (1:1)
    uploads = copy_tree_if_exists(UPLOADS_SRC, stage / "uploads")
    meta["sources"]["uploads"] = uploads
    print(f"[uploads]     {len(uploads)} file(s)")

    # 2. Transcripts (raw, for Claude to compact)
    transcripts = copy_tree_if_exists(TRANSCRIPTS_SRC, stage / "transcripts_raw")
    meta["sources"]["transcripts_raw"] = transcripts
    print(f"[transcripts] {len(transcripts)} file(s)")

    # 3. Write meta
    (stage / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nStaged to: {stage}")

    # 4. Report what Claude still needs to add
    pending = ["instructions.md  — project instructions from Claude's context"]
    if transcripts:
        pending.append("chat_history.md  — compacted summary of transcripts_raw/")
    else:
        pending.append("chat_history.md  — (no transcripts found; write placeholder)")

    print("\nClaude must still add:")
    for p in pending:
        print(f"  {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
