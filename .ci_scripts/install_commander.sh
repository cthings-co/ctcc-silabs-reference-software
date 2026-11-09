#!/usr/bin/env bash
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0
# Install a SHA-256-pinned Silicon Labs Commander on the GitHub Actions HOST,
# before starting the large Zephyr container. The workspace is mounted inside
# the container, so the command is available to Zephyr/CMake there as well.
set -euo pipefail

: "${GITHUB_WORKSPACE:?}"

if [ "$(uname -s)" != Linux ] || [ "$(uname -m)" != x86_64 ]; then
  echo 'ERROR: This pinned Simplicity Commander archive targets Linux x86_64' >&2
  exit 1
fi

base="$GITHUB_WORKSPACE/.ci_commander"
archive="$base/Commander_linux_x86_64_1v16p4b1564.tar.zst"
partial="$archive.partial"
url='https://github.com/SiliconLabsSoftware/arduino/releases/download/2.0.0/Commander_linux_x86_64_1v16p4b1564.tar.zst'
sha256='0d1a2136a824c2f3e9953573502cb80ff459647f41df04d17a30e42140432f8a'

mkdir -p "$base/bin" "$base/unpacked"
trap 'rm -f "$partial"' EXIT

echo 'Downloading pinned Simplicity Commander 1.16.4 from Silicon Labs GitHub release'
curl --fail --location --silent --show-error \
  --retry 2 --retry-all-errors --retry-delay 3 \
  --connect-timeout 20 --max-time 180 \
  --output "$partial" "$url"
mv -f -- "$partial" "$archive"

printf '%s  %s\n' "$sha256" "$archive" | sha256sum --check --status || {
  echo 'ERROR: Simplicity Commander SHA-256 mismatch' >&2
  exit 1
}
echo 'PASS: Simplicity Commander archive SHA-256 verified'

if ! command -v zstd >/dev/null 2>&1; then
  echo 'zstd is missing from the host; installing it for tar extraction'
  sudo apt-get update -qq
  sudo apt-get install -y -qq zstd
fi

tar --zstd --no-same-owner -xf "$archive" -C "$base/unpacked"
commander="$(find "$base/unpacked" -type f -name commander -print -quit)"
if [ -z "$commander" ]; then
  echo 'ERROR: Simplicity Commander binary not found in pinned archive' >&2
  find "$base/unpacked" -maxdepth 5 -type f -print >&2
  exit 1
fi

chmod u+x "$commander"
# Invoke the real file in-place so its adjacent libraries/resources stay findable.
printf -v executable '%q' "$commander"
printf '#!/usr/bin/env bash\nexec %s "$@"\n' "$executable" > "$base/bin/commander"
chmod u+x "$base/bin/commander"

"$base/bin/commander" --version
printf 'PASS: Commander preflight successful: %s\n' "$base/bin/commander"
