#!/usr/bin/env bash
# Silicon Labs adaptation of the reference nRF workspace preparation script.
set -euo pipefail

: "${GITHUB_WORKSPACE:?}"
: "${ZEPHYR_SDK_INSTALL_DIR:?}"

repo="$GITHUB_WORKSPACE"
west_root="$(dirname "$repo")"
venv="$HOME/venv"

# Check shared host-installed Commander inside the container before west update.
echo 'Checking Simplicity Commander inside the pinned Zephyr container'
"$repo/.ci_commander/bin/commander" --version

if [ ! -d "$ZEPHYR_SDK_INSTALL_DIR" ]; then
  echo "ERROR: pinned Zephyr SDK missing: $ZEPHYR_SDK_INSTALL_DIR" >&2
  exit 1
fi

python3 -m venv "$venv"
# shellcheck disable=SC1091
source "$venv/bin/activate"
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install 'west==1.5.0'

cd "$west_root"
west init -l "$repo"

# Shallow update, with bounded retries, matching the nRF reference approach.
for attempt in 1 2 3; do
  if west update --narrow -o=--depth=1; then
    break
  fi
  if [ "$attempt" -eq 3 ]; then
    echo 'ERROR: west update failed three times' >&2
    exit 1
  fi
  sleep "$((attempt * 10))"
done

west zephyr-export
python3 -m pip install -r "$west_root/zephyr/scripts/requirements.txt"
python3 -m pip install -e "$west_root/bootloader/mcuboot/scripts"
python3 -m pip install intelhex

bash "$repo/scripts/apply-mcuboot-patches.sh"

python3 -m pip freeze --local > "$repo/python-requirements.lock"
echo 'PASS: Silicon Labs west workspace prepared'
