#!/usr/bin/env python3
"""make.fun entry: World news of 23 November 2026 in one image.

Copies the pre-rendered poster (entry.png, 1024x1024) byte-for-byte to the
output directory. Before copying, it validates the PNG signature so a
corrupt or non-PNG source file is refused instead of submitted; after
copying, it verifies the copy with a size + SHA-256 check.

Standard library only. No network access, no randomness, no clock reads:
given the same entry.png the output is deterministic.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

# PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"

    expected_size = SOURCE.stat().st_size
    expected_sha = sha256_of(SOURCE)

    with open(SOURCE, "rb") as handle:
        signature = handle.read(len(PNG_SIGNATURE))
    if signature != PNG_SIGNATURE:
        print(
            "invalid PNG signature: entry.png is not a PNG file",
            file=sys.stderr,
        )
        return 1

    shutil.copyfile(SOURCE, dest)

    actual_size = dest.stat().st_size
    actual_sha = sha256_of(dest)
    if actual_size != expected_size:
        print(
            f"size mismatch: copied {actual_size} bytes, "
            f"expected {expected_size}",
            file=sys.stderr,
        )
        return 1
    if actual_sha != expected_sha:
        print(
            f"sha256 mismatch: copied {actual_sha}, expected {expected_sha}",
            file=sys.stderr,
        )
        return 1
    print(f"wrote {dest} ({actual_size} bytes, sha256 {actual_sha})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
