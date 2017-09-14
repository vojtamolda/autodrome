# Distributed under the MIT license.

#.rst:
# FindATS
# -------
#
# CMake module for detecting American Truck Simulator (ATS) installation.
#
# This module sets the following variables in the project::
#   ATS_FOUND        - True if ATS found on the system.
#   ATS_EXECUTABLE   - ATS game executable.
#   ATS_INSTALL_DIR  - The root directory containing ATS installation.
#   ATS_PLUGIN_DIR   - Directory for storing ATS game plugins.
#   ATS_USER_DIR     - User settings directory.
#
# The ATS::ATS target is available for import. For example liek this::
#   <code>
#     find_package(ATS)
#     install(my_plugin ${ATS_PLUGIN_DIR})
#   </code>
#

include(FindPackageMessage)


if (APPLE)
    set(ATS_INSTALL_DIR
            "$ENV{HOME}/Library/Application Support/Steam/steamapps/common/American Truck Simulator/"
            CACHE FILEPATH "ATS installation directory")
    set(ATS_USER_DIR
            "$ENV{HOME}/Library/Application Support/American Truck Simulator/"
            CACHE FILEPATH "ATS user preferences directory")

    set(ATS_EXECUTABLE_SUFFIX
            "American Truck Simulator.app/Contents/MacOS/")
endif ()
if (UNIX AND NOT APPLE)
    set(ATS_INSTALL_DIR
            "$ENV{HOME}/.steam/steam/SteamApps/common/American Truck Simulator/"
            CACHE FILEPATH "ATS installation directory")
    set(ATS_USER_DIR
            "$ENV{HOME}/local/share/American Truck Simulator/"
            CACHE FILEPATH "ATS user preferences directory")
    set(ATS_EXECUTABLE_SUFFIX
            bin/)
endif ()
if (WIN32)
    set(ATS_INSTALL_DIR
            "C:/Program Files/Steam/steamapps/common/American Truck Simulator/"
            CACHE FILEPATH "ATS installation directory")
    set(ATS_USER_DIR
            "$ENV{HOMEDRIVE}$ENV{HOMEPATH}/Documents/American Truck Simulator/"
            CACHE FILEPATH "ATS user preferences directory")
    set(ATS_EXECUTABLE_SUFFIX
            bin/)
endif ()
set(ATS_PLUGIN_DIR
        "${ATS_INSTALL_DIR}/${ATS_EXECUTABLE_SUFFIX}/plugins/")

find_program(ATS_EXECUTABLE
        TARGETS amtrucks
        HINTS ${ATS_INSTALL_DIR}
        PATH_SUFFIXES ${ATS_EXECUTABLE_SUFFIX}
        DOC "ATS game executable")

if (ATS_EXECUTABLE)
    set(ATS_FOUND
            TRUE)
    find_package_message(ATS
            "Found ATS: ${ATS_INSTALL_DIR}"
            "${ATS_INSTALL_DIR}")
else ()
    set(ATS_FOUND
            FALSE)
    find_package_message(ATS
            "ATS not found: ${ATS_INSTALL_DIR}"
            "${ATS_INSTALL_DIR}")
endif ()
