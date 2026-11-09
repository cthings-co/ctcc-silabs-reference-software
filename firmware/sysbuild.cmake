# Copyright (c) 2026 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0

# Additional configuration for the application image.
if(SB_CONFIG_BOOTLOADER_MCUBOOT)
  get_property(image_scripts TARGET ${DEFAULT_IMAGE} PROPERTY IMAGE_CONF_SCRIPT)

  list(APPEND image_scripts
    "${CMAKE_CURRENT_LIST_DIR}/sysbuild/image_size.cmake"
  )

  set_property(TARGET ${DEFAULT_IMAGE}
    PROPERTY IMAGE_CONF_SCRIPT "${image_scripts}"
  )
endif()

# Require the project-specific fixes in the pinned MCUboot checkout.
if(SB_CONFIG_BOOTLOADER_MCUBOOT)
  find_package(Git REQUIRED)

  set(mcuboot_dir
    "${CMAKE_CURRENT_LIST_DIR}/../../bootloader/mcuboot"
  )

  foreach(patch_name IN ITEMS
      mcuboot-console-init-once.patch
      mcuboot-uart-upload-size.patch
  )
    set(mcuboot_patch
      "${CMAKE_CURRENT_LIST_DIR}/../patches/${patch_name}"
    )

    execute_process(
      COMMAND "${GIT_EXECUTABLE}" -C "${mcuboot_dir}"
        apply --reverse --check "${mcuboot_patch}"
      RESULT_VARIABLE patch_check_result
      OUTPUT_QUIET
      ERROR_QUIET
    )

    if(NOT patch_check_result STREQUAL "0")
      message(FATAL_ERROR
        "Required MCUboot patch is missing: ${patch_name}. "
        "Run ./scripts/apply-mcuboot-patches.sh from the repository root "
        "and rebuild."
      )
    endif()

    message(STATUS "MCUboot patch verified: ${patch_name}")
  endforeach()
endif()
