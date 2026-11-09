#!/usr/bin/env python3
"""Verify actual DTS flow-control state for firmware and MCUboot images."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 3 or sys.argv[2] not in ("on", "off"):
    raise SystemExit("usage: verify_uart_flow.py <sysbuild-dir> <on|off>")

build_dir = Path(sys.argv[1])
expect_firmware = sys.argv[2] == "on"

for image, expected in (("firmware", expect_firmware), ("mcuboot", False)):
    dts = build_dir / image / "zephyr" / "zephyr.dts"
    if not dts.is_file():
        raise SystemExit(f"FAIL: Missing {dts}")

    content = dts.read_text(encoding="utf-8")
    usart = re.search(
        r"^\s*usart0:\s*[^\n]*\{\s*\n(.*?)^\s*\};",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if usart is None:
        raise SystemExit(f"FAIL: USART0 node missing from {dts}")

    enabled = bool(re.search(r"\bhw-flow-control\s*;", usart.group(1)))
    if enabled != expected:
        raise SystemExit(
            f"FAIL: {image} flow control is {'ON' if enabled else 'OFF'}, "
            f"expected {'ON' if expected else 'OFF'}"
        )
    print(f"PASS: {image} UART hardware flow control {'ON' if enabled else 'OFF'}")
