cmake_minimum_required(VERSION 3.10)
project(XPlaneThrottlePlugin)

add_library(XPlaneThrottle SHARED src/plugin.cpp)

target_include_directories(XPlaneThrottle PRIVATE ${CMAKE_SOURCE_DIR}/XPLM-SDK/CHeaders/XPLM)
target_link_libraries(XPlaneThrottle ws2_32)

set_target_properties(XPlaneThrottle PROPERTIES PREFIX "" SUFFIX ".xpl")