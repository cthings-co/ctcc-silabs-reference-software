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

The MGM240P board supports MCUboot as the open-source bootloader for
signed firmware images and UART-based serial recovery.

MCUboot is integrated using Zephyr sysbuild and supports both board variants:

- `mgm240p/mgm240pa32vnn/mpcie`
- `mgm240p/mgm240pa32vnn/m2_fc`

### Flash layout

The MGM240P has 1536 KiB of internal flash, divided into three partitions:

| Partition | Start address | Size |
|---|---|---|
| MCUboot | `0x08000000` | 128 KiB |
| Primary image (slot 0) | `0x08020000` | 696 KiB |
| Secondary image (slot 1) | `0x080CE000` | 704 KiB |
| Storage | `0x0817E000` | 8 KiB |

The partition definitions are located in
`boards/ct/mgm240p/mgm240p_common.dtsi`.

MCUboot uses the boot partition, while the application is linked
to the primary image partition.

### Building with MCUboot

Run the following commands from the initialized Silicon Labs West workspace.

For the mPCIe board:

```bash
west build --sysbuild \
  -b mgm240p/mgm240pa32vnn/mpcie \
  -d build/mcuboot_mpcie \
  ctcc-silabs-reference-software/firmware \
  -p always
```

For the M.2 flow-control board:

```bash
west build --sysbuild \
  -b mgm240p/mgm240pa32vnn/m2_fc \
  -d build/mcuboot_m2_fc \
  ctcc-silabs-reference-software/firmware \
  -p always
```

The build generates separate MCUboot and application images.

For the M.2 variant, the relevant artifacts include:

```text
build/mcuboot_m2_fc/mcuboot/zephyr/zephyr.signed.hex
build/mcuboot_m2_fc/firmware/zephyr/zephyr.signed.hex
build/mcuboot_m2_fc/firmware/zephyr/zephyr.signed.bin
```

The signed BIN is used for UART firmware updates.

Simplicity Commander must be installed and available in `PATH` for
the Silicon Labs bootloader signing step.

### Firmware signing

Use the Python environment configured for the Zephyr workspace.
The `imgtool` verification and HEX-merging commands require Python
dependencies, including `intelhex`.

Install `intelhex` in the active Python environment if needed:

```bash
python3 -m pip install intelhex
```

Verify that the package is available:

```bash
python3 -c "from intelhex import IntelHex; print('IntelHex OK')"
```


The application image is signed automatically during the sysbuild process.

For development, MCUboot uses the default test key:

```text
bootloader/mcuboot/root-ec-p256.pem
```

This key is intended for development and testing only.
Production firmware must use a securely managed signing key.

To verify the signed M.2 application:

```bash
python3 bootloader/mcuboot/scripts/imgtool.py verify \
  --key bootloader/mcuboot/root-ec-p256.pem \
  build/mcuboot_m2_fc/firmware/zephyr/zephyr.signed.bin
```

Successful verification reports:

```text
Image was correctly validated
```

### Initial programming

For initial programming, MCUboot and the signed application must
both be present in internal flash.

The two HEX files can be combined using Python's `intelhex` package:

```bash
python3 - <<'PY'
from intelhex import IntelHex
from pathlib import Path

build = Path("build/mcuboot_m2_fc")

bootloader = IntelHex(str(build / "mcuboot/zephyr/zephyr.signed.hex"))
application = IntelHex(str(build / "firmware/zephyr/zephyr.signed.hex"))

combined = IntelHex()
combined.merge(bootloader, overlap="error")
combined.merge(application, overlap="error")

assert 0x08000000 <= bootloader.minaddr()
assert bootloader.maxaddr() < 0x08020000

assert 0x08020000 <= application.minaddr()
assert application.maxaddr() < 0x080D0000

combined.write_hex_file(str(build / "mcuboot_firmware_combined.hex"))
PY
```

For mPCIe, replace `build/mcuboot_m2_fc` with `build/mcuboot_mpcie`.

Program the combined HEX using J-Flash Lite with:

- Device: `EFR32MG24BxxxF1536`
- Interface: SWD
- Speed: 100 kHz

After programming, reset the board.

### UART serial recovery

MCUboot supports firmware updates over USART0.

The configuration is located in:

```text
firmware/sysbuild/mcuboot/prj.conf
```

Serial recovery is enabled with a five-second startup window.

For the M.2 variant, USART0 uses:

| Signal | Pin |
|---|---|
| TX | PA5 |
| RX | PA6 |
| RTS | PB0 |
| CTS | PB1 |

The UART baud rate is 115200.

On the tested M.2 jig, the CP2102N USB-to-UART adapter appears
as `/dev/ttyUSB0`.

The following command requests the current image information:

```bash
mcumgr \
  --conntype serial \
  --connstring "dev=/dev/ttyUSB0,baud=115200" \
  --timeout 1 \
  --tries 20 \
  image list
```

Reset the board while the command is running to enter MCUboot
serial recovery mode.

When MCUboot enters serial recovery, the application does not run,
so the application LED stops blinking.

### Uploading firmware over UART

With the current MCUboot serial recovery configuration, firmware
is uploaded directly to the primary application partition (slot 0).

**Warning:** This replaces the existing application. An interrupted
upload may require recovery using J-Link.

Prepare and verify a new signed firmware image before uploading it.

While MCUboot is in serial recovery mode, upload the signed BIN:

```bash
mcumgr \
  --conntype serial \
  --connstring "dev=/dev/ttyUSB0,baud=115200" \
  --timeout 5 \
  --tries 5 \
  image upload -w 1 \
  build/mcuboot_m2_fc/firmware/zephyr/zephyr.signed.bin
```

After a successful upload, reset the board to start the new firmware.

The secondary slot and swap-based update mechanism are configured,
but slot-1 update and rollback behavior have not yet been validated.

### Hardware validation

The following tests have been performed on physical MGM240P hardware:

| Test | mPCIe | M.2 flow control |
|---|---|---|
| MCUboot sysbuild | Passed | Passed |
| Signed image verification | Passed | Passed |
| Initial programming through J-Link | Passed | Passed |
| Application boot through MCUboot | Passed | Passed |
| LED blinking | Passed | Passed |
| UART serial recovery | Passed | Passed |
| Firmware update through UART | Passed | Passed |

UART firmware updates have been successfully verified on both board variants.

On the M.2 board, firmware version `0.0.0+0` was replaced with
version `0.0.1+0` using MCUboot serial recovery and MCUmgr.
The LED toggle interval changed from 1000 ms to 200 ms.

On the mPCIe board, firmware version `0.0.0+0` was replaced with
version `0.0.2+0` using MCUboot serial recovery and MCUmgr.
The updated application started successfully and the LED blinked
faster, consistent with the configured 500 ms toggle interval.

Recovery without a valid application and slot-1 swap/rollback
behavior remain untested.

## Continuous Integration (CI)

The repository uses GitHub Actions to automatically build, test,
validate, and package firmware for the supported MGM240P variants.

The CI configuration consists of two workflows:

- `.github/workflows/build-firmwares.yml` - main CI workflow.
- `.github/workflows/release-firmwares.yml` - reusable workflow
  responsible for testing, building, validating, and packaging firmware.

### Workflow triggers

The CI pipeline runs automatically when:

- Changes are pushed to the `main` branch.
- A pull request is opened or updated.

The pipeline can also be started manually using the
**Run workflow** button in GitHub Actions.

### Build configurations

The pipeline builds three firmware configurations:

| Configuration | Board | UART flow control |
|---|---|---|
| `mpcie-no-flow` | `mgm240p/mgm240pa32vnn/mpcie` | Disabled |
| `m2-fc-no-flow` | `mgm240p/mgm240pa32vnn/m2_fc` | Disabled |
| `m2-fc-flow` | `mgm240p/mgm240pa32vnn/m2_fc` | Enabled (RTS/CTS) |

The M.2 configurations use dedicated Devicetree overlays:

- `firmware/overlays/uart-fc-off.overlay`
- `firmware/overlays/uart-fc-on.overlay`

Firmware builds run inside a pinned Zephyr CI Docker image.

Workspace dependencies are selected using the `west.yml` manifest,
which references Silicon Labs SDK `v2026.6.0`.

The CI environment uses Zephyr SDK toolchain version `1.0.1`.

### Automated validation

The pipeline performs the following validation steps:

1. Run Python unit tests.
2. Build firmware for all three configurations.
3. Verify firmware artifacts and SHA-256 checksums.
4. Package the verified firmware artifacts.

Python unit tests are executed using:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Firmware builds use the scripts located in `.ci_scripts/`.

The pipeline installs the pinned Silicon Labs Simplicity Commander
and prepares the Zephyr workspace before building.

The packaging job runs only after the Python unit tests and
all firmware builds have completed successfully.

### Firmware artifacts

Each successful firmware build uploads its artifacts to GitHub Actions.

Individual firmware artifact sets are retained for **14 days**.

After all builds complete, the packaging job creates a ZIP archive
containing the verified firmware artifacts.

The archive follows this naming convention:

```text
ctcc-silabs-firmwares-<ref>-<commit>-<date>.zip
```

Where:

- `<ref>` is the sanitized Git branch or reference name.
- `<commit>` is the first eight characters of the commit SHA.
- `<date>` is the UTC date in `YYYYMMDD` format.

A corresponding SHA-256 checksum file is generated:

```text
ctcc-silabs-firmwares-<ref>-<commit>-<date>.zip.sha256
```

The final package is uploaded as a GitHub Actions artifact named
`firmware-package`.

The final package is retained for **90 days**.

### Downloading firmware artifacts

To download generated firmware:

1. Open the repository on GitHub.
2. Navigate to the **Actions** tab.
3. Select the **CTCC Silicon Labs Firmwares CI** workflow.
4. Open a successful workflow run.
5. Locate the **Artifacts** section.
6. Download the `firmware-package` artifact.
7. Extract the downloaded artifact to access the firmware ZIP
   and its SHA-256 checksum file.

Verify the firmware ZIP archive using:

```bash
sha256sum -c <firmware-package-name>.zip.sha256
```

Replace `<firmware-package-name>` with the actual archive filename,
without the `.zip` extension.

### CI limitations

The CI pipeline verifies firmware builds, runs Python unit tests,
and checks generated artifacts.

It does not replace hardware validation on physical MGM240P devices.

MCUboot startup, firmware flashing, and UART-based firmware updates
must be validated separately on the target hardware.

Instructions for MCUboot, initial programming, firmware signing,
and UART recovery are provided in the **Open Bootloader** section.

## Firmware releases

The current GitHub Actions configuration generates downloadable
workflow artifacts.

It does not automatically publish firmware to GitHub Releases.

Firmware packages can be downloaded from successful GitHub Actions
runs and used for further validation or release preparation.
