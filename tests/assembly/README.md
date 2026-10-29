# MGM240P Assembly Tests

Hardware assembly tests for CTHINGS MGM240P connectivity cards.

The tests use Zephyr Ztest firmware and a Python host-side test
runner to verify basic hardware functionality.

Two board variants are supported:

- MGM240P mPCIe
- MGM240P M.2 Key-E with UART hardware flow control

Both variants use the same Python test runner.

## Requirements

- Zephyr RTOS 4.4.x development environment
- Zephyr SDK
- Python 3 with pyserial
- MGM240P connectivity card
- Compatible programming JIG
- USB connection to the CP2102N UART interface
- MCUboot installed on the target board

UART communication uses 115200 baud.

## Building the firmware

Run the commands from the Zephyr workspace root.

### mPCIe

Run from the Zephyr workspace root:

    west build --no-sysbuild -b mgm240p/mgm240pa32vnn/mpcie -d build/assembly_mpcie ctcc-silabs-reference-software/tests/assembly -p always

### M.2 Key-E

Run from the Zephyr workspace root:

    west build --no-sysbuild -b mgm240p/mgm240pa32vnn/m2_fc -d build/assembly_m2_fc ctcc-silabs-reference-software/tests/assembly -p always

## Firmware installation

The assembly firmware uses MCUboot.

Build the appropriate board variant, sign the application
with an MCUboot-compatible key, and upload it using mcumgr.

Verify that the intended image is active before testing.

## Running the tests

Run from the repository root.

For mPCIe:

    python3 tests/assembly/tools/run_assembly.py --board mpcie

For M.2 Key-E:

    python3 tests/assembly/tools/run_assembly.py --board m2_fc

For detailed Zephyr output, add --verbose.

The runner automatically detects the CP2102N serial port
when exactly one matching device is available.

## Operator procedure

1. Connect the appropriate MGM240P card and JIG.
2. Start the Python test runner.
3. Press PERST when requested.
4. Confirm each LED using y/n followed by Enter.
5. Follow the instructions for the GPIO button test.
6. Check the final PASS/FAIL result.

## Hardware test coverage

### mPCIe

- PERST reset verification
- UART TX/RX (PA5/PA6)
- LED_WWAN (PA8)
- LED_WLAN (PA7)
- GPIO input transitions (PD0)

LED_WPAN is not connected to the MGM240P MCU.

### M.2 Key-E

- PERST reset verification
- UART TX/RX (PA5/PA6)
- LED1 (PA8)
- LED2 (PA7)
- W_DISABLE1 input (PD0)
- UART RTS/CTS runtime configuration
- MGM240P RTS to host CTS signaling
- Host RTS to MGM240P CTS flow control
- MCU-to-host UART transmission integrity

Full data-integrity stress testing in the reverse UART
direction has not been performed.

PERST verification is performed by the Python runner,
not by a separate Zephyr Ztest case.

## Known limitations

### mPCIe WAKE / W_DISABLE discrepancy

According to the schematics, W_DISABLE is connected
to MGM240P PD0, while WAKE is not connected to the MCU.

During testing with the available mPCIe JIG, PD0
responded to the physical button labeled WAKE rather
than W_DISABLE.

The Python runner therefore instructs the operator
to press WAKE on this JIG.

The cause of this discrepancy is not confirmed.

The test verifies PD0 input transitions.
It does not verify the physical W_DISABLE button.

### M.2 unused buttons

WAKE and W_DISABLE2 are not connected to MGM240P GPIOs.
They are marked N/A.

### COEX1 / COEX2

COEX1 is connected to PD2.
COEX2 is connected to PD1.

Both signals are available on the JIG connectors,
but electrical loopback testing was not performed.

They are marked NOT TESTED.

## Results

PASS: All required tests passed.
FAIL / INCOMPLETE: A required test failed or is missing.
N/A: Functionality is not available on this card.
NOT TESTED: Functionality exists but was not verified.

A final PASS does not imply that N/A or NOT TESTED
functions were validated.

## Files

- CMakeLists.txt: Zephyr application build configuration
- prj.conf: Zephyr configuration
- src/main.c: Zephyr Ztest firmware
- tools/run_assembly.py: Python host-side test runner
