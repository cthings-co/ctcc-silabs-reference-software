#!/usr/bin/env python3
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Validate a firmware release tag against firmware/VERSION."""

import re
import sys
from pathlib import Path

from check_version import parse_version


def validate_tag(tag, version):
    match = re.fullmatch(
        r"v(0|[1-9][0-9]*)\."
        r"(0|[1-9][0-9]*)\."
        r"(0|[1-9][0-9]*)",
        tag,
    )

    if match is None:
        raise ValueError(
            "Release tag must use the format vMAJOR.MINOR.PATCH"
        )

    tag_version = tuple(int(value) for value in match.groups())

    if version[3] != 0:
        raise ValueError(
            "VERSION_TWEAK must be 0 for a release tag"
        )

    if tag_version != version[:3]:
        raise ValueError(
            f"Tag version {tag_version} does not match "
            f"firmware version {version[:3]}"
        )


def main():
    if len(sys.argv) != 2:
        print("Usage: check_release_tag.py vMAJOR.MINOR.PATCH")
        return 2

    try:
        version = parse_version(
            Path("firmware/VERSION").read_text()
        )
        validate_tag(sys.argv[1], version)

    except (ValueError, OSError) as error:
        print(f"FAIL: {error}")
        return 1

    print(f"PASS: Release tag {sys.argv[1]} matches firmware/VERSION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
