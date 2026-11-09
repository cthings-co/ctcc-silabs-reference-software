# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Tests for firmware release tag validation."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / ".ci_scripts"),
)

from check_release_tag import validate_tag


class TestReleaseTag(unittest.TestCase):

    def test_matching_tag_accepted(self):
        validate_tag("v0.1.0", (0, 1, 0, 0))

    def test_mismatched_tag_rejected(self):
        with self.assertRaises(ValueError):
            validate_tag("v0.2.0", (0, 1, 0, 0))

    def test_invalid_format_rejected(self):
        with self.assertRaises(ValueError):
            validate_tag("release-0.1.0", (0, 1, 0, 0))

    def test_nonzero_tweak_rejected(self):
        with self.assertRaises(ValueError):
            validate_tag("v0.1.0", (0, 1, 0, 1))


if __name__ == "__main__":
    unittest.main()
