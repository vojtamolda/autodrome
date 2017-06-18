# Distributed under the MIT license.

#.rst:
# FindSCSSDK
# ---------
#
# CMake module to find SCS Game Telemetry SDK (SCSSDK).
#
# This module sets the following variables in the project::
#   SCSSDK_FOUND         - True if SCSSDK is found on the system.
#   SCSSDK_INCLUDE_DIRS  - Include directory containing SCSSDK header files.
#
# Example usage::
#   <code>
#     find_package(SCSSDK REQUIRED)
#     set_include_dirs(my_executable ${SCSSDK_INCLUDE_DIRS})
#   </code>
#

include(FindPackageMessage)

set(SCSSDK_INSTALL_DIR
        "${CMAKE_SOURCE_DIR}/scssdk/"
        CACHE FILEPATH "SCS Game Telemetry SDK installation directory")
set(SCSSDK_INCLUDE_DIRS
        "${SCSSDK_INSTALL_DIR}/include/")

if (IS_DIRECTORY ${SCSSDK_INSTALL_DIR})
    set(SCSSDK_FOUND
            TRUE)
    find_package_message(ATS
            "Found SCSSDK: ${SCSSDK_INSTALL_DIR}"
            "${SCSSDK_INSTALL_DIR}")
else ()
    set(SCSSDK_FOUND
            FALSE)
    find_package_message(SCSSDK
            "SCSSDK not found: ${SCSSDK_INSTALL_DIR}"
            "${SCSSDK_INSTALL_DIR}")
endif()
