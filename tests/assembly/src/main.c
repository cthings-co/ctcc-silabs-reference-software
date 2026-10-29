/*
 * Copyright (c) 2026 CTHINGS.CO
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/ztest.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/console/console.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>

/* Board-specific test labels */
#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_MPCIE)

#define BOARD_NAME "MGM240P mPCIe"
#define LED1_NAME "LED_WWAN"
#define LED2_NAME "LED_WLAN"

#elif defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_M2_FC)

#define BOARD_NAME "MGM240P M.2 Key-E"
#define LED1_NAME "LED1"
#define LED2_NAME "LED2"

#else
#error "Unsupported MGM240P board variant"
#endif

/* Common MCU LED connections */
#define LED1_NODE DT_ALIAS(led0)
#define LED2_NODE DT_ALIAS(led1)

static const struct gpio_dt_spec led1 =
    GPIO_DT_SPEC_GET(LED1_NODE, gpios);

static const struct gpio_dt_spec led2 =
    GPIO_DT_SPEC_GET(LED2_NODE, gpios);

/* Ignore newline characters left in the input buffer. */
static int read_answer(void)
{
    int c;

    do {
        c = console_getchar();
    } while (c == '\r' || c == '\n');

    return c;
}

/* UART TX/RX test */
ZTEST(assembly_base_tests, hello_console)
{
    printk("\nCTHINGS MGM240P Assembly Tests\n");

    for (int i = 0; i < 3; i++) {
        printk("Hello Console Test!\n");
    }

    printk("Press any key to confirm UART communication...\n");

    int c = read_answer();

    zassert_true(c >= 0, "UART input failed");

    printk("UART communication confirmed!\n");
}

/* Interactive test for one LED */
static void test_led(const struct gpio_dt_spec *led,
                     const char *name,
                     char expected_key)
{
    zassert_true(gpio_is_ready_dt(led),
                 "%s GPIO device not ready", name);

    zassert_ok(gpio_pin_configure_dt(led, GPIO_OUTPUT_INACTIVE),
               "%s GPIO configuration failed", name);

    zassert_ok(gpio_pin_set_dt(led, 1),
               "%s could not be turned on", name);

    printk("\n%s should be ON.\n", name);
    printk("Press '%c' if the LED is ON.\n", expected_key);
    printk("Press 'n' if the LED is not working.\n");

    int c = read_answer();

    zassert_ok(gpio_pin_set_dt(led, 0),
               "%s could not be turned off", name);

    zassert_equal(c, expected_key,
                  "%s was not confirmed", name);

    printk("%s confirmed!\n", name);
}

/* LED1: PA8 */
ZTEST(assembly_base_tests, led1)
{
    test_led(&led1, LED1_NAME, '1');
}

/* LED2: PA7 */
ZTEST(assembly_base_tests, led2)
{
    test_led(&led2, LED2_NAME, '2');
}


#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_M2_FC)

/* Verify runtime RTS/CTS configuration on M.2. */
ZTEST(assembly_base_tests, uart_rts_cts_config)
{
    const struct device *uart =
        DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

    struct uart_config original;
    struct uart_config flow;
    struct uart_config current;

    zassert_true(device_is_ready(uart), "UART device not ready");

    zassert_ok(uart_config_get(uart, &original),
               "Cannot read UART configuration");

    flow = original;
    flow.flow_ctrl = UART_CFG_FLOW_CTRL_RTS_CTS;

    int ret = uart_configure(uart, &flow);

    zassert_ok(ret, "Cannot enable RTS/CTS");

    ret = uart_config_get(uart, &current);

    /* Restore the original configuration before checking results. */
    int restore_ret = uart_configure(uart, &original);

    zassert_ok(restore_ret, "Cannot restore UART configuration");
    zassert_ok(ret, "Cannot read updated UART configuration");

    zassert_equal(current.flow_ctrl,
                  UART_CFG_FLOW_CTRL_RTS_CTS,
                  "RTS/CTS configuration was not applied");

    printk("RTS/CTS runtime configuration confirmed!\n");
}

#endif


#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_M2_FC)

/*
 * Send a predictable stream with RTS/CTS enabled.
 * The host-side Python script verifies the physical handshake.
 */
ZTEST(assembly_base_tests, uart_rts_cts_tx_stream)
{
    const struct device *uart =
        DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

    struct uart_config original;
    struct uart_config flow;

    zassert_true(device_is_ready(uart), "USART0 not ready");
    zassert_ok(uart_config_get(uart, &original),
               "Cannot get UART configuration");

    flow = original;
    flow.flow_ctrl = UART_CFG_FLOW_CTRL_RTS_CTS;

    zassert_ok(uart_configure(uart, &flow),
               "Cannot enable RTS/CTS");

    printk("\nFLOW_STREAM_BEGIN\n");

    k_msleep(500);

    for (int i = 0; i < 2500; i++) {
        uart_poll_out(uart, 'A' + (i % 26));
        k_msleep(4);
    }

    printk("\nFLOW_STREAM_END\n");
    k_msleep(100);

    zassert_ok(uart_configure(uart, &original),
               "Cannot restore UART configuration");

    printk("UART stream sent; host verifies hardware flow control.\n");
}

#endif


#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_M2_FC)

/*
 * Observe MGM240P RTS on the host CTS input.
 * The host validates the actual signal transition.
 */
ZTEST(assembly_base_tests, uart_rts_cts_rx_pause)
{
    const struct device *uart =
        DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

    struct uart_config original;
    struct uart_config flow;

    zassert_true(device_is_ready(uart), "UART not ready");
    zassert_ok(uart_config_get(uart, &original),
               "Cannot read UART configuration");

    flow = original;
    flow.flow_ctrl = UART_CFG_FLOW_CTRL_RTS_CTS;

    zassert_ok(uart_configure(uart, &flow),
               "Cannot enable RTS/CTS");

    /*
     * Stop draining the hardware RX FIFO temporarily.
     * This is a test-only operation.
     */
    uart_irq_rx_disable(uart);

    printk("\nFLOW_RX_PAUSED\n");

    k_msleep(6000);

    uart_irq_rx_enable(uart);

    printk("\nFLOW_RX_RESUMED\n");

    zassert_ok(uart_configure(uart, &original),
               "Cannot restore UART configuration");

    printk("RX pause test completed; check host result.\n");
}


#endif


#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_MPCIE) || \
    defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_M2_FC)

#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_MPCIE)
#define W_DISABLE_LABEL "W_DISABLE"
#else
#define W_DISABLE_LABEL "W_DISABLE1"
#endif

/* Both card variants connect W_DISABLE to PD0 (active low). */
#define SIGNALS_NODE DT_NODELABEL(mgm240p_signals)

static const struct gpio_dt_spec w_disable_gpio =
    GPIO_DT_SPEC_GET(SIGNALS_NODE, w_disable_gpios);

static bool wait_gpio_state(int expected, int timeout_ms)
{
    for (int elapsed = 0; elapsed < timeout_ms; elapsed += 20) {
        int state = gpio_pin_get_dt(&w_disable_gpio);

        if (state == expected) {
            return true;
        }

        if (state < 0) {
            return false;
        }

        k_msleep(20);
    }

    return false;
}

ZTEST(assembly_base_tests, w_disable)
{
    zassert_true(gpio_is_ready_dt(&w_disable_gpio),
                 "W_DISABLE GPIO not ready");

    zassert_ok(gpio_pin_configure_dt(
                   &w_disable_gpio, GPIO_INPUT | GPIO_PULL_UP),
               "Cannot configure " W_DISABLE_LABEL "");

    printk("\n[BOARD] Make sure " W_DISABLE_LABEL " is released.\n");

    zassert_true(wait_gpio_state(0, 30000),
                 "" W_DISABLE_LABEL " is still active when released");

    printk("[BOARD] Press and hold " W_DISABLE_LABEL " (30 seconds)...\n");

    zassert_true(wait_gpio_state(1, 30000),
                 "" W_DISABLE_LABEL " press not detected");

    printk("[BOARD] " W_DISABLE_LABEL " press detected.\n");
    printk("[BOARD] Release " W_DISABLE_LABEL "...\n");

    zassert_true(wait_gpio_state(0, 30000),
                 "" W_DISABLE_LABEL " release not detected");

    printk("[BOARD] " W_DISABLE_LABEL " release detected.\n");
}

#endif




static void *setup_assembly(void)
{
    console_init();

    printk("\n=== CTHINGS MGM240P Assembly Tests ===\n");
    printk("Board: %s\n", BOARD_NAME);

#if defined(CONFIG_BOARD_MGM240P_MGM240PA32VNN_MPCIE)
    printk("LED_WPAN: N/A - not connected on MGM240P mPCIe card\n");
#endif

    return NULL;
}

ZTEST_SUITE(assembly_base_tests, NULL, setup_assembly, NULL, NULL, NULL);
