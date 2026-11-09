#!/usr/bin/env python3
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Check signed MCUboot image size for swap-with-offset."""

import argparse
from pathlib import Path


def parse_size(value):
    return int(value, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--primary-slot-size", type=parse_size, required=True)
    parser.add_argument("--secondary-slot-size", type=parse_size, required=True)
    parser.add_argument("--sector-size", type=parse_size, required=True)
    parser.add_argument("--trailer-size", type=parse_size, required=True)
    args = parser.parse_args()

    sector = args.sector_size
    if sector <= 0 or args.trailer_size < 0:
        parser.error("Invalid sector or trailer size")

    trailer = (
        (args.trailer_size + sector - 1) // sector
    ) * sector

    max_size = min(
        args.primary_slot_size - trailer,
        args.secondary_slot_size - trailer - sector,
    )

    if max_size <= 0:
        parser.error("Flash layout leaves no room for an image")

    actual_size = args.image.stat().st_size

    print(f"Signed image size: {actual_size} bytes")
    print(f"Maximum allowed:   {max_size} bytes")

    if actual_size > max_size:
        print("ERROR: Signed image exceeds MCUboot capacity")
        return 1

    print("OK: Signed image fits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
