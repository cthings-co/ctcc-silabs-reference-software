"""Host-side regression test for the MCUboot UART image-size guard."""

from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]

MCUBOOT_SOURCE = (
    ROOT.parent
    / "bootloader/mcuboot/boot/boot_serial/src/boot_serial.c"
)

source = MCUBOOT_SOURCE.read_text()

# Extract the actual size-check block from our patched MCUboot.
message = 'BOOT_LOG_ERR("Image exceeds MCUboot maximum size");'
message_pos = source.index(message)

guard_start = source.rfind(
    "#if defined(MCUBOOT_SWAP_USING_OFFSET)", 0, message_pos
)

assert guard_start >= 0, "Size guard not found"

guard_end = source.index("#endif", message_pos) + len("#endif")
guard = source[guard_start:guard_end]

# Verify that the guard appears before the Flash erase operation.
erase_pos = source.index(
    "rc = boot_erase_region(fap, 0, area_size, false);",
    guard_end,
)

assert guard_end < erase_pos, "Size guard must precede Flash erase"

# Compile the extracted guard with simulated MCUboot dependencies.
c_code = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define MCUBOOT_SWAP_USING_OFFSET 1
#define MCUBOOT_SERIAL_DIRECT_IMAGE_UPLOAD 1
#define MCUBOOT_SERIAL_IMG_GRP_SLOT_INFO 1

#define BOOT_LOG_ERR(...) ((void)0)

struct image_max_size {
    bool calculated;
    uint32_t max_size;
};

static struct image_max_size sizes[] = {
    { true, 704512u }
};

static const struct image_max_size *boot_get_max_app_size(void)
{
    return sizes;
}

static unsigned erase_count;

static int test_upload(uint32_t img_size_tmp)
{
    const uint32_t area_size = 720896u;

    if (img_size_tmp > area_size) {
        goto out_invalid_data;
    }

""" + guard + r"""

    /* Simulated erase immediately after the actual size guard. */
    erase_count++;
    return 0;

out_invalid_data:
    return -1;
}

static void check(uint32_t size, int expected_result,
                  unsigned expected_erases)
{
    erase_count = 0;

    assert(test_upload(size) == expected_result);
    assert(erase_count == expected_erases);
}

int main(void)
{
    /* Maximum permitted image size. */
    check(704512u, 0, 1);

    /* One byte above the maximum: reject before erase. */
    check(704513u, -1, 0);

    /* Full slot size: reject before erase. */
    check(720896u, -1, 0);

    /* Unknown maximum size: reject before erase. */
    sizes[0].calculated = false;
    check(1000u, -1, 0);

    puts("PASS: MCUboot UART size-guard regression tests");
    return 0;
}
"""

with tempfile.TemporaryDirectory() as tmp:
    c_file = Path(tmp) / "test_guard.c"
    executable = Path(tmp) / "test_guard"

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

print("PASS: Guard is positioned before the Flash erase operation")