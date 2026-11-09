#!/usr/bin/env bash
# MGM240P version of the nRF reference .ci_scripts/build_sdk.sh.
set -euo pipefail

: "${GITHUB_WORKSPACE:?}"
: "${ZEPHYR_SDK_INSTALL_DIR:?}"
: "${BOARD:?}"
: "${BUILD_NAME:?}"
: "${EXPECTED_FLOW_CONTROL:?}"

source "$HOME/venv/bin/activate"
export PATH="$GITHUB_WORKSPACE/.ci_commander/bin:$PATH"
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr

# CMake in Silicon Labs Zephyr requires Commander even for MCUboot sysbuild.
commander --version

west_root="$(dirname "$GITHUB_WORKSPACE")"
build="$west_root/build/$BUILD_NAME"
cd "$west_root"

cmake_args=()
if [ -n "${OVERLAY:-}" ]; then
  test -f "$GITHUB_WORKSPACE/$OVERLAY" || {
    echo "ERROR: Missing UART overlay: $OVERLAY" >&2
    exit 1
  }
  cmake_args+=("-Dfirmware_DTC_OVERLAY_FILE=$GITHUB_WORKSPACE/$OVERLAY")
fi

west build --sysbuild \
  -b "$BOARD" \
  -d "$build" \
  "$GITHUB_WORKSPACE/firmware" \
  -p always -- "${cmake_args[@]}"

signed="$build/firmware/zephyr/zephyr.signed.bin"
mcuboot_hex="$build/mcuboot/zephyr/zephyr.hex"
firmware_hex="$build/firmware/zephyr/zephyr.signed.hex"

for file in "$signed" "$mcuboot_hex" "$firmware_hex"; do
  test -s "$file" || { echo "ERROR: Missing artifact: $file" >&2; exit 1; }
done

python3 "$west_root/bootloader/mcuboot/scripts/imgtool.py" verify \
  --key "$west_root/bootloader/mcuboot/root-ec-p256.pem" \
  "$signed"

# Image size is validated during the Zephyr build using Devicetree
# partition sizes by the check_mcuboot_signed_image target.
image_size="$(stat -c '%s' "$signed")"

python3 "$GITHUB_WORKSPACE/.ci_scripts/verify_uart_flow.py" \
  "$build" "$EXPECTED_FLOW_CONTROL"

dest="$GITHUB_WORKSPACE/artifacts/$BUILD_NAME"
mkdir -p "$dest"
cp "$signed" "$dest/${BUILD_NAME}_firmware.signed.bin"
cp "$firmware_hex" "$dest/${BUILD_NAME}_firmware.signed.hex"
cp "$mcuboot_hex" "$dest/${BUILD_NAME}_mcuboot.hex"
cp "$GITHUB_WORKSPACE/python-requirements.lock" "$dest/${BUILD_NAME}_python-requirements.lock"

# The reference nRF CI also publishes a merged programming HEX.
# Reject overlapping addresses rather than silently overwriting either image.
python3 - "$mcuboot_hex" "$firmware_hex" "$dest/${BUILD_NAME}_merged.hex" <<'PY_MERGE'
from intelhex import IntelHex
import sys
boot = IntelHex(sys.argv[1])
firmware = IntelHex(sys.argv[2])
boot.merge(firmware, overlap="error")
boot.write_hex_file(sys.argv[3])
print("PASS: non-overlapping MCUboot + firmware programming HEX")
PY_MERGE

cp "$build/firmware/zephyr/zephyr.dts" "$dest/${BUILD_NAME}_firmware.dts"
cp "$build/mcuboot/zephyr/zephyr.dts" "$dest/${BUILD_NAME}_mcuboot.dts"

( cd "$dest" && find . -type f ! -name SHA256SUMS -printf '%P\0' \
  | LC_ALL=C sort -z | xargs -0 -r sha256sum > SHA256SUMS )
( cd "$dest" && sha256sum -c --quiet SHA256SUMS )

echo "PASS: $BUILD_NAME signed firmware verified and packaged ($image_size bytes)"
