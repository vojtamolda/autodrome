# Distributed under the MIT license.

#.rst:
# FindCPPZMQ
# ---------
#
# CMake module to find C++ bindings for ZMQ library (CPPZMQ).
#
# This module sets the following variables in the project::
#   CPPZMQ_FOUND         - True if CPPZMQ is found on the system.
#   CPPZMQ_INCLUDE_DIRS  - Include directory containing CPPZMQ header files.
#
# Example usage::
#   <code>
#     find_package(CPPZMQ REQUIRED)
#     set_include_dirs(my_executable ${CPPZMQ_INCLUDE_DIRS})
#   </code>
#

include(FindPackageMessage)

set(CPPZMQ_INSTALL_DIR
        "${CMAKE_SOURCE_DIR}/cppzmq/"
        CACHE FILEPATH "ZMQ C++ bindings installation directory")

if (EXISTS "${CPPZMQ_INSTALL_DIR}/zmq.hpp")
    set(CPPZMQ_FOUND
            TRUE)
    set(CPPZMQ_INCLUDE_DIRS
            ${CPPZMQ_INSTALL_DIR})
    find_package_message(ATS
            "Found CPPZMQ: ${CPPZMQ_INSTALL_DIR}"
            "${CPPZMQ_INSTALL_DIR}")
else ()
    set(CPPZMQ_FOUND
            FALSE)
    find_package_message(CPPZMQ
            "CPPZMQ not found: ${CPPZMQ_INSTALL_DIR}"
            "${CPPZMQ_INSTALL_DIR}")
endif()
