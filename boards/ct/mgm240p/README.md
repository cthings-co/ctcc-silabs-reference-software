# CTHINGS MGM240P Board Support

Zephyr board support for CTHINGS MGM240P connectivity cards.

## Hardware variants

Two physical card variants are supported:

- **mPCIe** (`mpcie`)
- **M.2 Key-E with UART flow control** (`m2_fc`)

Both variants use the EFR32MG24B210F1536IM48 SoC
and share the same common board configuration.

## Pinout

The pinout is based on the CTHINGS MGM240P card schematics.

Pin assignments are documented from the MCU perspective.

The MCU pinout must not be confused with card connector
signals or programming JIG signals.

### Common MCU pin assignments

The following signals are present on both MGM240P card variants.

| MCU pin | Signal | Function | Zephyr representation |
|---|---|---|---|
| PA1 | SWCLK | SWD clock | Documented, not configured as GPIO |
| PA2 | SWDIO | SWD data | Documented, not configured as GPIO |
| PA3 | TRACEDATA0 | Trace data | Documented, not configured as GPIO |
| PA4 | TRACECLK | Trace clock | Documented, not configured as GPIO |
| PA5 | MGM_TX | USART0 TX | Pinctrl |
| PA6 | MGM_RX | USART0 RX | Pinctrl |
| PA7 | LED2 | LED control | GPIO LED (`led1`) |
| PA8 | LED1 | LED control | GPIO LED (`led0`) |
| PD0 | W_DISABLE | Wireless disable | Custom board signal |
| PD1 | COEX2 | Coexistence signal | Custom board signal |
| PD2 | COEX1 | Coexistence signal | Custom board signal |

### M.2 flow-control variant

The M.2 Key-E variant (`m2_fc`) provides two additional
USART0 signals.

| MCU pin | Signal | Function | Zephyr representation |
|---|---|---|---|
| PB0 | MGM_RTS | USART0 RTS | Variant-specific pinctrl |
| PB1 | MGM_CTS | USART0 CTS | Variant-specific pinctrl |

These pins are configured in `mgm240p-m2-fc-pinctrl.dtsi`.

The mPCIe variant does not use these pins for UART flow control.

The M.2 board definition describes the physical RTS/CTS connections,
but hardware flow control is not enabled by default.

### Other MCU pins

The following MCU GPIO pins have no external connections shown
in either MGM240P card schematic.

| MCU pin | mPCIe | M.2 flow control | Zephyr configuration |
|---|---|---|---|
| PA0 | Not connected | Not connected | Not configured |
| PB2 | Not connected | Not connected | Not configured |
| PB3 | Not connected | Not connected | Not configured |
| PB4 | Not connected | Not connected | Not configured |
| PC0 | Not connected | Not connected | Not configured |
| PC1 | Not connected | Not connected | Not configured |
| PC2 | Not connected | Not connected | Not configured |
| PC3 | Not connected | Not connected | Not configured |
| PC4 | Not connected | Not connected | Not configured |
| PC5 | Not connected | Not connected | Not configured |
| PC6 | Not connected | Not connected | Not configured |
| PC7 | Not connected | Not connected | Not configured |
| PD3 | Not connected | Not connected | Not configured |

These pins are not assigned to application peripherals
by the current board definition.

The absence of an external connection does not mean that
the MCU pins are unavailable for other purposes.

### Other hardware connections

The MGM240P card schematics also show connections for:

- RF output and antenna.
- MCU power supply and ground.
- MCU reset circuitry.
- SWD and trace debugging interfaces.

These are not ordinary application GPIO assignments.

The PERST card connector signal is handled through external
reset circuitry and must not be treated as a normal MCU GPIO.

COEX0 is not included because its connection to the MGM240P
MCU has not been established.
