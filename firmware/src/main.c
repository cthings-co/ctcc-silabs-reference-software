#include <zephyr/dfu/mcuboot.h>
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>

#define LED_NODE DT_ALIAS(led0)

static const struct gpio_dt_spec led =
    GPIO_DT_SPEC_GET(LED_NODE, gpios);

int main(void)
{
    int rc;

    if (!gpio_is_ready_dt(&led)) {
        printk("LED device is not ready\n");
        return 0;
    }

    rc = gpio_pin_configure_dt(&led, GPIO_OUTPUT_INACTIVE);
    if (rc != 0) {
        printk("LED initialization failed: %d\n", rc);
        return 0;
    }

    /* Confirm a test image after successful basic initialization. */
    if (!boot_is_img_confirmed()) {
        rc = boot_write_img_confirmed();

        if (rc != 0) {
            printk("MCUboot image confirmation failed: %d\n", rc);
            return 0;
        }
        printk("MCUboot image confirmed\n");
    }

    while (1) {
        printk("CTHINGS Silicon Labs reference firmware\n");
        gpio_pin_toggle_dt(&led);
        k_msleep(1000);
    }

    return 0;
}
