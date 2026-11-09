#!/usr/bin/env python3
# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

"""Host-side assembly test runner for MGM240P mPCIe and M.2 variants."""

import time
import serial

PAYLOAD_LENGTH = 2500
MIN_PRE_PAUSE = 80


def receive_for(ser, seconds, data):
    stop = time.monotonic() + seconds
    start = len(data)

    while time.monotonic() < stop and len(data) < PAYLOAD_LENGTH:
        remaining = PAYLOAD_LENGTH - len(data)
        data.extend(ser.read(min(128, remaining)))

    return len(data) - start



def flow_rx_test(ser):
    """Observe host CTS while the board RX FIFO is not drained."""

    print("\n[HOST] Testing MGM240P RTS -> PC CTS...", flush=True)

    initial_ready = ser.cts
    print(f"[HOST] Initial CTS ready: {initial_ready}", flush=True)

    blocked = False

    # Send a small number of bytes, observing CTS after each one.
    # Do not continue transmitting once CTS is deasserted.
    for _ in range(16):
        if not ser.cts:
            blocked = True
            break

        ser.write(b"R")
        time.sleep(0.05)

        if not ser.cts:
            blocked = True
            break

    print(f"[HOST] CTS deasserted: {blocked}", flush=True)

    # The firmware automatically restores RX interrupts.
    resumed = False
    deadline = time.monotonic() + 9

    while time.monotonic() < deadline:
        if blocked and ser.cts:
            resumed = True
            break

        time.sleep(0.02)

    print(f"[HOST] CTS asserted again: {resumed}", flush=True)

    success = initial_ready and blocked and resumed

    print(
        "[HOST] MGM RTS -> PC CTS signal test: "
        + ("PASS" if success else "FAIL"),
        flush=True
    )

    return success


def flow_test(ser):
    data = bytearray()
    deadline = time.monotonic() + 5

    # Receive initial data before stopping transmission.
    while len(data) < MIN_PRE_PAUSE and time.monotonic() < deadline:
        remaining = PAYLOAD_LENGTH - len(data)
        data.extend(ser.read(min(128, remaining)))

    print(f"\n[HOST] Before pause: {len(data)} bytes", flush=True)

    # Stop MCU transmission by deasserting the host RTS.
    ser.rts = False

    try:
        # Allow previously buffered USB/UART data to arrive.
        receive_for(ser, 0.4, data)

        # During this window transmission should be stopped.
        quiet_bytes = receive_for(ser, 0.8, data)

    finally:
        # Always unblock the MCU.
        ser.rts = True

    print(
        f"[HOST] Bytes received during quiet window: {quiet_bytes}",
        flush=True
    )

    # Receive the remaining data after resuming transmission.
    deadline = time.monotonic() + 25

    while len(data) < PAYLOAD_LENGTH and time.monotonic() < deadline:
        remaining = PAYLOAD_LENGTH - len(data)
        data.extend(ser.read(min(128, remaining)))

    expected = bytes(
        ord("A") + (i % 26)
        for i in range(PAYLOAD_LENGTH)
    )

    complete = len(data) == PAYLOAD_LENGTH
    intact = bytes(data) == expected
    stopped = quiet_bytes == 0

    success = complete and intact and stopped

    print(
        f"[HOST] Data complete: {complete} "
        f"({len(data)}/{PAYLOAD_LENGTH})",
        flush=True
    )

    print(
        f"[HOST] Data integrity: {'PASS' if intact else 'FAIL'}",
        flush=True
    )

    print(
        "[HOST] TX flow control (PC RTS -> MGM CTS): "
        f"{'PASS' if success else 'FAIL'}",
        flush=True
    )

    return success



def confirm_led(ser, name, key):
    while True:
        answer = input(
            f"[HOST] Does {name} light up? [y/n, then Enter]: "
        ).strip().lower()

        if answer in ("y", "yes"):
            ser.write(key)
            return

        if answer in ("n", "no"):
            ser.write(b"n")
            return

        print("[HOST] Please enter y or n.")



def main():
    import argparse
    import glob

    parser = argparse.ArgumentParser(
        description="CTHINGS MGM240P assembly test runner"
    )

    parser.add_argument(
        "--board",
        required=True,
        choices=["mpcie", "m2_fc"],
        help="Board variant"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed Zephyr test logs"
    )

    args = parser.parse_args()

    ports = sorted(glob.glob(
        "/dev/serial/by-id/*CP2102N*"
    ))

    if len(ports) != 1:
        raise SystemExit(
            f"Expected exactly one CP2102N port, found: {ports}"
        )

    port = ports[0]

    expected_tests = {
        "hello_console",
        "led1",
        "led2",
        "w_disable",
    }



    if args.board == "m2_fc":
        expected_tests.update({
            "uart_rts_cts_config",
            "uart_rts_cts_tx_stream",
            "uart_rts_cts_rx_pause",
        })

    aliases = {
        "led1_wwan": "led1",
        "led2_wlan": "led2",
        "w_disable1": "w_disable",
    }

    passed_tests = set()
    hardware_ok = None
    flow_rx_ok = None
    summary_ok = False
    board_confirmed = False
    perst_ok = False

    print("\n=== CTHINGS MGM240P ASSEMBLY TESTS ===")
    print(f"[HOST] Board: {args.board}")
    print(f"[HOST] Port: {port}")

    with serial.Serial(
        port,
        115200,
        timeout=0.1,
        rtscts=False
    ) as ser:

        ser.rts = True
        ser.reset_input_buffer()

        print("\n[HOST] Ready.")
        print("[HOST] Press PERST on the JIG to start testing.")
        print("[HOST] Waiting for firmware output...\n")

        boot_banner_seen = False
        deadline = time.monotonic() + 180

        while time.monotonic() < deadline:
            line = ser.readline().decode(errors="replace")

            if not line:
                continue

            if "Booting Zephyr OS build" in line:
                boot_banner_seen = True

            # Hide internal firmware instructions from the operator.
            hidden_prompts = (
                "Press any key to confirm UART communication",
                "Press '1' if the LED is ON",
                "Press '2' if the LED is ON",
                "Press 'n' if the LED is not working",
            )

            # Operator mode: show only useful test information.
            # All lines are still processed by the test runner.
            if args.verbose:
                if not any(prompt in line for prompt in hidden_prompts):
                    print(line, end="", flush=True)

            elif line.strip().startswith("PASS - "):
                name = line.split("PASS - ", 1)[1].split()[0]

                if name != "hello_console":
                    label = (
                        "WAKE button (PD0)"
                        if args.board == "mpcie" and name == "w_disable"
                        else name
                    )
                    print(f"[HOST] PASS: {label}", flush=True)

            elif line.strip().startswith("FAIL - "):
                name = line.split("FAIL - ", 1)[1].split()[0]
                print(f"[HOST] FAIL: {name}", flush=True)

            elif (
                "should be ON." in line
                or line.startswith("[BOARD] ")
                or "Assertion failed" in line
                or "not detected" in line
                or "PROJECT EXECUTION FAILED" in line
            ):
                display_line = line

                if args.board == "mpcie" and line.startswith("[BOARD] "):
                    display_line = line.replace("W_DISABLE", "WAKE")

                print(display_line, end="", flush=True)

            if "Board: MGM240P mPCIe" in line:
                if args.board != "mpcie":
                    raise RuntimeError("Wrong board selected")
                board_confirmed = True

            elif "mPCIe JIG:" in line:
                if args.board != "mpcie":
                    raise RuntimeError("Wrong board selected")
                board_confirmed = True

            elif "Board: MGM240P M.2 Key-E" in line:
                if args.board != "m2_fc":
                    raise RuntimeError("Wrong board selected")
                board_confirmed = True

            if boot_banner_seen and board_confirmed and not perst_ok:
                perst_ok = True
                print(
                    "[HOST] PERST: PASS (board restart detected)",
                    flush=True
                )

            if " PASS - " in line:
                name = line.split("PASS - ", 1)[1].split()[0]
                passed_tests.add(aliases.get(name, name))

                if name == "hello_console":
                    print("[HOST] UART TX/RX: PASS", flush=True)

            if "Press any key to confirm UART communication" in line:
                print("[HOST] Testing UART TX/RX automatically...", flush=True)
                ser.write(b"a")

            elif "Press '1' if the LED is ON" in line:
                name = "LED_WWAN" if args.board == "mpcie" else "LED1"
                confirm_led(ser, name, b"1")

            elif "Press '2' if the LED is ON" in line:
                name = "LED_WLAN" if args.board == "mpcie" else "LED2"
                confirm_led(ser, name, b"2")

            elif "FLOW_RX_PAUSED" in line:
                flow_rx_ok = flow_rx_test(ser)

            elif "FLOW_STREAM_BEGIN" in line:
                if args.board != "m2_fc":
                    raise RuntimeError("Unexpected RTS/CTS test")
                hardware_ok = flow_test(ser)

            elif "PROJECT EXECUTION SUCCESSFUL" in line:
                summary_ok = True
                break

            elif "PROJECT EXECUTION FAILED" in line:
                break

        ser.rts = True

    missing = expected_tests - passed_tests

    success = (
        summary_ok
        and board_confirmed
        and perst_ok
        and not missing
        and (
            args.board == "mpcie"
            or (hardware_ok is True and flow_rx_ok is True)
        )
    )

    if args.board == "m2_fc":
        print("\n[HOST] WAKE: N/A (not connected to MGM240P)")
        print("[HOST] W_DISABLE2: N/A (not connected to MGM240P)")

    print("\n[HOST] COEX1/COEX2: NOT TESTED (no loopback connection)")

    print("\n=== FINAL ASSEMBLY TEST RESULT ===")

    if missing:
        print(f"[HOST] Missing PASS results: {sorted(missing)}")

    if not board_confirmed:
        print("[HOST] Board identification was not confirmed")

    if success:
        print("[HOST] RESULT: PASS")
    else:
        print("[HOST] RESULT: FAIL / INCOMPLETE")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
