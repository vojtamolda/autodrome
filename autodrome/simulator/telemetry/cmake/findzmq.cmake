# Distributed under the MIT license.

#.rst:
# FindZMQ
# -------
#
# CMake module to find Zero Message Queue (ZMQ) library.
#
# On windows are are looking for the libraries in the default locations when the
# user follows the build instructions on the package website.   On Linux we are
# using pkg_config to provide a starting point to look for the package.  If
# the default method doesn't succeed, one can either add the  location of
# ZeroMQ in the CMAKE_PREFIX_PATH variable, or set the  ZeroMQ_INSTALL_DIR.
#
# This module sets the following variables in the project::
#   ZMQ_FOUND         - True if ZMQ found on the system.
#   ZMQ_INCLUDE_DIRS  - Include directory containing ZMQ header files.
#   ZMQ_LIBRARIES     - ZMQ libraries
#
# The ZMQ::ZMQ target is available for import and linking. For example like this::
#   <code>
#     find_package(ZMQ REQUIRED)
#     target_link_libraries(my_executable ZMQ)
#   </code>
#

include(FindPackageHandleStandardArgs)

if (UNIX)
    find_package(PkgConfig QUIET)
    pkg_search_module(ZMQ_PKG libzmq)
endif ()
if (WIN32)
    # Lame check for this: http://zeromq.org/distro:microsoft-windows
    file(GLOB ZMQ_PKG_INCLUDE_DIRS "C:/Program Files/ZeroMQ*/include/")
    file(GLOB ZMQ_PKG_LIBRARY_DIRS "C:/Program Files/ZeroMQ*/lib/")
endif ()

find_path(ZMQ_INCLUDE_DIRS
        zmq.h
        HINTS ${ZMQ_INSTALL_DIR} ${ZMQ_PKG_INCLUDE_DIRS}
        PATH_SUFFIXES include/
        DOC "Include directory for ZMQ library")

find_library(ZMQ_LIBRARIES
        NAMES zmq libzmq
        PATH_SUFFIXES lib/
        HINTS ${ZMQ_INSTALL_DIR} ${ZMQ_PKG_LIBRARY_DIRS}
        DOC "ZMQ library binary")

find_package_handle_standard_args(ZMQ
        REQUIRED_VARS ZMQ_LIBRARIES ZMQ_INCLUDE_DIRS)
