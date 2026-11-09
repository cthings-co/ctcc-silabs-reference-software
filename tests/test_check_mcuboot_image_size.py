# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for the MCUboot signed-image size validator."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_mcuboot_image_size.py"
)


class TestMCUbootImageSize(unittest.TestCase):

    def run_validator(self, image_size):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "test_image.bin"

            with image.open("wb") as output:
                output.truncate(image_size)

            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(image),
                    "--primary-slot-size", "0xb0000",
                    "--secondary-slot-size", "0xb0000",
                    "--sector-size", "0x2000",
                    "--trailer-size", "0x2000",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_small_image_accepted(self):
        result = self.run_validator(22596)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_image_at_limit_accepted(self):
        result = self.run_validator(704512)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_image_above_limit_rejected(self):
        result = self.run_validator(704513)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", result.stdout)


if __name__ == "__main__":
    unittest.main()
