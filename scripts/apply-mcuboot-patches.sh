#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mcuboot_dir="$repo_dir/../bootloader/mcuboot"

# Verify the pinned MCUboot revision.
expected_revision="40fbecd0"
actual_revision=$(git -C "$mcuboot_dir" rev-parse --short=8 HEAD)

if [ "$actual_revision" != "$expected_revision" ]; then
    echo "ERROR: Unexpected MCUboot revision: $actual_revision"
    exit 1
fi

# Apply all project-required MCUboot patches.
for patch_name in \
    mcuboot-console-init-once.patch \
    mcuboot-uart-upload-size.patch
do
    patch="$repo_dir/patches/$patch_name"

    if git -C "$mcuboot_dir" apply --reverse --check "$patch" 2>/dev/null; then
        echo "Already applied: $patch_name"

    elif git -C "$mcuboot_dir" apply --check "$patch" 2>/dev/null; then
        git -C "$mcuboot_dir" apply "$patch"
        echo "Applied: $patch_name"

    else
        echo "ERROR: Cannot apply $patch_name"
        exit 1
    fi
done

echo "All MCUboot patches verified."
