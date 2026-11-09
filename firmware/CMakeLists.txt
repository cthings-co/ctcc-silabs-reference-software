cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ctcc_silabs_reference_firmware)

target_sources(app PRIVATE src/main.c)

# Check the signed application size after MCUboot signing.
if(CONFIG_BOOTLOADER_MCUBOOT)

  # Read the actual Flash partition sizes from DeviceTree.
  dt_nodelabel(slot0_node NODELABEL "slot0_partition" REQUIRED)
  dt_nodelabel(slot1_node NODELABEL "slot1_partition" REQUIRED)

  dt_reg_size(primary_slot_size PATH "${slot0_node}")
  dt_reg_size(secondary_slot_size PATH "${slot1_node}")

  # Read the Flash erase-block size.
  dt_chosen(flash_node PROPERTY "zephyr,flash")

  if(NOT flash_node)
    message(FATAL_ERROR "Cannot determine the Zephyr Flash device")
  endif()

  dt_prop(erase_block_size
    PATH "${flash_node}"
    PROPERTY "erase-block-size"
    REQUIRED
  )

  # The sysbuild ROM_END_OFFSET correction currently assumes
  # an 8 KiB Flash erase sector.
  if(NOT erase_block_size EQUAL 8192)
    message(FATAL_ERROR
      "MGM240P MCUboot sysbuild requires an 8192-byte Flash erase sector. "
      "Update firmware/sysbuild/image_size.cmake for the new geometry."
    )
  endif()

  # ROM_END_OFFSET includes MCUboot's estimated image footer
  # plus one additional sector for swap-with-offset.
  math(EXPR mcuboot_footer_estimate
    "${CONFIG_ROM_END_OFFSET} - ${erase_block_size}"
  )

  math(EXPR two_erase_blocks "${erase_block_size} * 2")

  # MCUboot's estimate includes the sector-aligned trailer and
  # signing overhead. If it reaches two erase blocks, we can
  # no longer safely assume a one-sector trailer.
  if(mcuboot_footer_estimate LESS erase_block_size
      OR mcuboot_footer_estimate GREATER_EQUAL two_erase_blocks)
    message(FATAL_ERROR
      "MCUboot footer reservation is outside the expected range. "
      "Review the trailer-size calculation for swap-with-offset."
    )
  endif()

  message(STATUS
    "MCUboot Flash layout: "
    "primary=${primary_slot_size}, "
    "secondary=${secondary_slot_size}, "
    "erase=${erase_block_size}"
  )

  add_custom_target(check_mcuboot_signed_image ALL
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/check_mcuboot_image_size.py"
      "${PROJECT_BINARY_DIR}/zephyr/zephyr.signed.bin"
      --primary-slot-size ${primary_slot_size}
      --secondary-slot-size ${secondary_slot_size}
      --sector-size ${erase_block_size}
      --trailer-size ${erase_block_size}
    DEPENDS "${PROJECT_BINARY_DIR}/zephyr/zephyr.signed.bin"
    COMMENT "Checking signed MCUboot image size"
    VERBATIM
  )
endif()
