# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Regression test for MCUboot UART upload destination selection."""

from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]

MCUBOOT_SOURCE = (
    ROOT.parent
    / "bootloader/mcuboot/boot/boot_serial/src/boot_serial.c"
)

source = MCUBOOT_SOURCE.read_text()

# Extract the actual image-selection block from MCUboot.
marker = "/* Use image number only from packet with offset == 0. */"
marker_pos = source.index(marker)

start = source.index(
    "if (img_chunk_off == 0) {",
    marker_pos,
)

brace_start = source.index("{", start)
depth = 0
end = None

for pos in range(brace_start, len(source)):
    if source[pos] == "{":
        depth += 1
    elif source[pos] == "}":
        depth -= 1

        if depth == 0:
            end = pos + 1
            break

assert end is not None, "Could not extract image-selection block"

selection_block = source[start:end]

assert "Direct upload requires an image number" in selection_block

# Verify selection occurs before the Flash destination is opened.
flash_open = source.index(
    "flash_area_open(flash_area_id_from_direct_image(img_num), &fap)",
    end,
)

assert end < flash_open, "Image selection must precede Flash access"

# Compile the extracted C code with simulated dependencies.
c_code = r"""
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

#define MCUBOOT_SERIAL_DIRECT_IMAGE_UPLOAD 1
#define BOOT_LOG_ERR(...) ((void)0)

static int select_image(uint32_t img_chunk_off,
                        uint32_t img_num_tmp,
                        uint32_t *selected)
{
    uint32_t img_num = 0;

""" + selection_block + r"""

    *selected = img_num;
    return 0;

out_invalid_data:
    return -1;
}

int main(void)
{
    uint32_t selected = UINT32_MAX;

    /* Missing destination must be rejected. */
    assert(select_image(0, UINT_MAX, &selected) != 0);

    /* Explicit image=2 must select the secondary slot. */
    assert(select_image(0, 2, &selected) == 0);
    assert(selected == 2);

    puts("PASS: Missing image number rejected");
    puts("PASS: Explicit image=2 selects secondary slot");

    return 0;
}
"""

with tempfile.TemporaryDirectory() as tmp:
    c_file = Path(tmp) / "test_destination.c"
    executable = Path(tmp) / "test_destination"

    c_file.write_text(c_code)

    subprocess.run(
        [
            "cc",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(c_file),
            "-o",
            str(executable),
        ],
        check=True,
    )

    subprocess.run([str(executable)], check=True)

print("PASS: Destination selection precedes Flash access")