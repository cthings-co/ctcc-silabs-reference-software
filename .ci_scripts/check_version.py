#!/usr/bin/env python3
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Check application version changes in pull requests."""

import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_FILE = "firmware/VERSION"
FIELDS = ("VERSION_MAJOR", "VERSION_MINOR", "PATCHLEVEL", "VERSION_TWEAK")


def git(*args, check=True):
    return subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        check=check,
    )


def parse_version(content):
    values = {}

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        match = re.fullmatch(r"([A-Z_]+)\s*=\s*(.*)", line)
        if not match:
            raise ValueError(f"Invalid VERSION line: {line}")

        key, value = match.groups()

        if key == "EXTRAVERSION":
            continue

        if key not in FIELDS or key in values:
            raise ValueError(f"Unexpected or duplicate field: {key}")

        if not value.isdigit() or not 0 <= int(value) <= 255:
            raise ValueError(f"Invalid value for {key}: {value}")

        values[key] = int(value)

    if set(values) != set(FIELDS):
        raise ValueError("VERSION file has missing required fields")

    return tuple(values[field] for field in FIELDS)


def main():
    base = os.environ.get("VERSION_BASE", "origin/main")
    head = os.environ.get("VERSION_HEAD", "HEAD")

    try:
        current = parse_version(Path(VERSION_FILE).read_text())

        old_file = git(
            "show", f"{base}:{VERSION_FILE}", check=False
        )

        if old_file.returncode != 0:
            print(f"PASS: Initial VERSION file: {current}")
            return 0

        previous = parse_version(old_file.stdout)

        changed = git(
            "diff", "--name-only", f"{base}...{head}",
            "--", "firmware/", "boards/", "dts/", "patches/"
        ).stdout.splitlines()

        if current < previous:
            print("FAIL: Firmware version decreased")
            return 1

        if changed and current == previous:
            print("FAIL: Firmware sources changed without version bump")
            for filename in changed:
                print(f"  {filename}")
            return 1

        print(f"PASS: Version {previous} -> {current}")
        return 0

    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
