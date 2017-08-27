# Distributed under the MIT license.

#.rst:
# FindETS2
# --------
#
# CMake module for detecting Euro Truck Simulator 2 (ETS2) installation.
#
# This module sets the following variables in the project::
#   ETS2_FOUND        - True if ETS2 found on the system.
#   ETS2_EXECUTABLE   - ETS2 game executable.
#   ETS2_INSTALL_DIR  - The root directory containing ETS2 installation.
#   ETS2_PLUGIN_DIR   - Directory for storing ETS2 game plugins.
#   ETS2_USER_DIR     - User settings directory.
#
# The ETS2::ETS2 target is available for import. For example liek this::
#   <code>
#     find_package(ETS2)
#     install(my_plugin ${ETS2_PLUGIN_DIR})
#   </code>
#

include(FindPackageMessage)


if (APPLE)
    set(ETS2_INSTALL_DIR
            "$ENV{HOME}/Library/Application Support/Steam/steamapps/common/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 installation directory")
    set(ETS2_USER_DIR
            "$ENV{HOME}/Library/Application Support/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 user preferences directory")
    set(ETS2_EXECUTABLE_SUFFIX
            "Euro Truck Simulator 2.app/Contents/MacOS/")
endif ()
if (UNIX AND NOT APPLE)
    set(ETS2_INSTALL_DIR
            "$ENV{HOME}/.steam/steam/SteamApps/common/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 installation directory")
    set(ETS2_USER_DIR
            "$ENV{HOME}/local/share/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 user preferences directory")
    set(ETS2_EXECUTABLE_SUFFIX
            bin/)
endif ()
if (WIN32)
    set(ETS2_INSTALL_DIR
            "C:/Program Files/Steam/steamapps/common/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 installation directory")
    set(ETS2_USER_DIR
            "$ENV{HOMEDRIVE}$ENV{HOMEPATH}/Documents/Euro Truck Simulator 2/"
            CACHE FILEPATH "ETS2 user preferences directory")
    set(ETS2_EXECUTABLE_SUFFIX
            bin/)
endif ()
set(ETS2_PLUGIN_DIR
        "${ETS2_INSTALL_DIR}/${ETS2_EXECUTABLE_SUFFIX}/plugins/")

find_program(ETS2_EXECUTABLE
        TARGETS eurotrucks2
        HINTS ${ETS2_INSTALL_DIR}
        PATH_SUFFIXES ${ETS2_EXECUTABLE_SUFFIX}
        DOC "ETS2 game executable")

if (ETS2_EXECUTABLE)
    set(ETS2_FOUND
            TRUE)
    find_package_message(ETS2
            "Found ETS2: ${ETS2_INSTALL_DIR}"
            "${ETS2_INSTALL_DIR}")
else ()
    set(ETS2_FOUND
            FALSE)
    find_package_message(ETS2
            "ETS2 not found: ${ETS2_INSTALL_DIR}"
            "${ETS2_INSTALL_DIR}")
endif ()
