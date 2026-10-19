# CTHINGS Silicon Labs Reference Software

Zephyr board support and reference firmware for CTHINGS Silicon Labs hardware.

## Supported hardware

- **CTHINGS MGM240P**
  - Module: MGM240PA32VNN
  - SoC family: Silicon Labs EFR32MG24
  - Flash: 1536 KiB
  - RAM: 256 KiB

Two hardware variants are supported:

- **mPCIe** (`mpcie`) — UART TX/RX.
- **M.2 Key-E** (`m2_fc`) — UART TX/RX with RTS/CTS connections.

Both variants share the same MCU and common board configuration.

See [MGM240P board documentation](boards/ct/mgm240p/README.md) for detailed pin assignments and signal descriptions.

## Development environment

The project uses Silicon Labs Simplicity SDK for Zephyr and a
repository-owned out-of-tree board definition.

The Silicon Labs SDK release is pinned to `v2026.6.0` in `west.yml`.
This release includes a Silicon Labs-maintained Zephyr 4.4.1 fork.

Tested environment:

- Silicon Labs Zephyr SDK v2026.6.0
- Zephyr v4.4.1 (Silicon Labs fork)
- West 1.5.0
- Zephyr SDK (toolchain) 1.0.1
- CMake 4.2.3
- Ninja 1.13.2

The following setup instructions are intended for Linux.

## Workspace setup

Create a workspace directory and clone this repository:

```bash
mkdir -p ~/ctcc-silabs-workspace
cd ~/ctcc-silabs-workspace

git clone https://github.com/cthings-co/ctcc-silabs-reference-software.git
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install West:

```bash
pip install west
```

Initialize the West workspace using this repository as the manifest repository:

```bash
west init -l ctcc-silabs-reference-software
west update
west zephyr-export
```

Install the Python dependencies required by Zephyr:

```bash
pip install -r zephyr/scripts/requirements.txt
```

The resulting workspace contains the Silicon Labs Zephyr SDK,
including the Silicon Labs-maintained Zephyr fork, HAL,
MCUboot, and other dependencies selected by the SDK manifest.

Activate the Python environment when starting a new terminal session:

```bash
cd ~/ctcc-silabs-workspace
source .venv/bin/activate
```

## Zephyr SDK

Download and install Zephyr SDK 1.0.1 from the official release:

https://github.com/zephyrproject-rtos/sdk-ng/releases/tag/v1.0.1

For Linux x86-64, download and extract the GNU SDK bundle:

```bash
cd ~

wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v1.0.1/zephyr-sdk-1.0.1_linux-x86_64_gnu.tar.xz

tar xf zephyr-sdk-1.0.1_linux-x86_64_gnu.tar.xz
```

Run the SDK setup script:

```bash
cd ~/zephyr-sdk-1.0.1
./setup.sh
```

The SDK installation only needs to be performed once.

For other operating systems or architectures, follow the official [Zephyr SDK installation instructions](https://docs.zephyrproject.org/latest/develop/toolchains/zephyr_sdk.html).

The SDK should be discoverable by Zephyr during configuration. A successful configuration prints messages similar to:

```text
Found host-tools: zephyr 1.0.1
Found toolchain: zephyr 1.0.1
```

## Build

Activate the Python environment and navigate to the workspace root:

```bash
cd ~/ctcc-silabs-workspace
source .venv/bin/activate
```

Build the mPCIe variant:

```bash
west build \
  -b mgm240p/mgm240pa32vnn/mpcie \
  -d build/mpcie \
  ctcc-silabs-reference-software/firmware \
  -p always
```

Build the M.2 flow-control variant:

```bash
west build \
  -b mgm240p/mgm240pa32vnn/m2_fc \
  -d build/m2_fc \
  ctcc-silabs-reference-software/firmware \
  -p always
```

The board definition is discovered automatically from the repository through `zephyr/module.yml`; no manual `BOARD_ROOT` argument is required.

During configuration, verify that Zephyr selects the requested MGM240P board variant (`mpcie` or `m2_fc`).

Build artifacts are generated in separate directories for each board variant:

- **mPCIe:** `build/mpcie/zephyr/`
- **M.2 flow control:** `build/m2_fc/zephyr/`

The generated files include:

```text
zephyr.elf
zephyr.bin
zephyr.hex
```

## Flashing

The reference firmware can be programmed using a SEGGER J-Link debugger and J-Flash Lite.

Connect the J-Link to the MGM240P SWD interface and ensure the target board is powered.

Open J-Flash Lite and configure:

| Setting | Value |
|---|---|
| Target device | `EFR32MG24BxxxF1536` |
| Target interface | SWD |
| Interface speed | 100 kHz |
| Internal program flash | Enabled |
| User Data Page | Disabled |
| Flash loader | Default |

Select the generated Intel HEX file for the appropriate board variant:

- **mPCIe:** `build/mpcie/zephyr/zephyr.hex`
- **M.2 flow control:** `build/m2_fc/zephyr/zephyr.hex`

Click **Program Device** and wait for programming to complete.

After programming, reset or power-cycle the board to start the application.

The mPCIe reference firmware has been successfully programmed and run using J-Link and J-Flash Lite.

## Reference firmware

The reference firmware prints:

```text
CTHINGS Silicon Labs reference firmware
```

and toggles the board LED periodically.

The application is intentionally minimal and serves as the baseline for additional functionality.

## Open Bootloader

MCUboot/Open Bootloader support will be added separately.
