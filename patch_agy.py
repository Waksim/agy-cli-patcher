#!/usr/bin/env python3
"""Build a patched copy of a known Antigravity CLI build."""

import argparse
import hashlib
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


ORIGINAL_SHA256 = "5e4b545bff4a83a93354fc50c54631cf3e8cd02e1a469087af00929f3fdc4d51"
GOOGLE_SIGNATURE = 'identifier "cli" and anchor apple generic and certificate leaf[subject.OU] = "EQHXZ8M8AV"'

# Field number 5, repeated message IneligibleTier, with its protobuf and JSON names.
TIER_DESCRIPTOR = (
    b"\x12\x60\x0a\x10ineligible_tiers\x18\x05\x20\x03\x28\x0b"
    b"\x32\x35.google.internal.cloud.code.v1internal.IneligibleTier"
    b"\x52\x0fineligibleTiers"
)
PATCHED_DESCRIPTOR = TIER_DESCRIPTOR.replace(b"ineligible", b"inexigible")


def build_copy(source: Path, output: Path) -> None:
    if sys.platform != "darwin" or platform.machine() != "arm64":
        raise ValueError("run this patcher with native Python on Apple Silicon macOS")
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"output already exists: {output}")

    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("expected the Google-signed Apple Silicon build of agy 1.5.3")
    subprocess.run(
        ["/usr/bin/codesign", "--verify", "--strict", f"-R={GOOGLE_SIGNATURE}", str(source)],
        check=True,
    )
    if original.count(TIER_DESCRIPTOR) != 1:
        raise ValueError("expected one ineligible_tiers descriptor")

    patched = original.replace(TIER_DESCRIPTOR, PATCHED_DESCRIPTOR, 1)
    with tempfile.TemporaryDirectory(prefix=".agy-patch-", dir=output.parent) as directory:
        staged = Path(directory) / "agy"
        staged.write_bytes(patched)
        staged.chmod(0o755)
        subprocess.run(
            ["/usr/bin/codesign", "--force", "--sign", "-", "--preserve-metadata=identifier", str(staged)],
            check=True,
        )
        subprocess.run(["/usr/bin/codesign", "--verify", "--strict", str(staged)], check=True)
        os.link(staged, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="original Google-signed agy")
    parser.add_argument("output", type=Path, help="path for the new executable")
    args = parser.parse_args()
    try:
        build_copy(args.source, args.output)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"patch_agy: {error}\n")
    print(f"Created {args.output}")


if __name__ == "__main__":
    main()
