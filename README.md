# CTHINGS Silicon Labs Reference Software

Zephyr board support and reference firmware for CTHINGS Silicon Labs hardware.

## Supported hardware

- **CTHINGS MGM240P**
  - Module: MGM240PA32VNN
  - SoC family: Silicon Labs EFR32MG24
  - Flash: 1536 KiB
  - RAM: 256 KiB

## Development environment

The project uses Silicon Labs Simplicity SDK for Zephyr and a
repository-owned out-of-tree board definition.

The Silicon Labs SDK release is pinned to `v2026.6.0` in `west.yml`.
This release includes a Silicon Labs-maintained Zephyr 4.4.1 fork.

Tested environment:

- West 1.5.0
- Zephyr SDK 1.0.1
- CMake 4.2.3
- Ninja 1.13.2

## Python environment

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install West:

```bash
pip install west
```

Install the Python dependencies required by Zephyr:

```bash
pip install -r zephyr/scripts/requirements.txt
'''

## Workspace setup

Create a workspace directory and clone this repository into it:

```bash
mkdir -p ~/ctcc-silabs-workspace
cd ~/ctcc-silabs-workspace

git clone https://github.com/cthings-co/ctcc-silabs-reference-software.git
```

Initialize the West workspace using this repository as the manifest repository:

```bash
west init -l ctcc-silabs-reference-software
west update
west zephyr-export
```

The resulting workspace contains the Silicon Labs Zephyr SDK,
including the Silicon Labs-maintained Zephyr fork, HAL,
MCUboot, and other dependencies selected by the SDK manifest.

## Zephyr SDK

Install Zephyr SDK 1.0.1.

The SDK should be discoverable by Zephyr during configuration. A successful configuration prints messages similar to:

```text
Found host-tools: zephyr 1.0.1
Found toolchain: zephyr 1.0.1
```

## Build

From the workspace root:

```bash
west build \
  -b mgm240p/mgm240pa32vnn \
  -d build/firmware \
  ctcc-silabs-reference-software/firmware \
  -p always
```

The board definition is discovered automatically from the repository through `zephyr/module.yml`; no manual `BOARD_ROOT` argument is required.

A successful configuration should identify:

```text
Board: mgm240p, qualifiers: mgm240pa32vnn
```

Build artifacts are generated under:

```text
build/firmware/zephyr/
```

including:

```text
zephyr.elf
zephyr.bin
zephyr.hex
```

## Reference firmware

The reference firmware prints:

```text
CTHINGS Silicon Labs reference firmware
```

and toggles the board LED periodically.

The application is intentionally minimal and serves as the baseline for additional functionality.

## Open Bootloader

MCUboot/Open Bootloader support will be added separately.
