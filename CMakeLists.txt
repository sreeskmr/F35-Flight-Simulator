cmake_minimum_required(VERSION 3.10)

# Project name and version
project(F35_Flight_Simulator VERSION 1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add executable
add_executable(f35_flightsim
    src/main.cpp
    src/throttle.cpp
    src/sensor.cpp
    # Add other source files here
)

# Include directories
target_include_directories(f35_flightsim PRIVATE include)

# Platform-specific libraries
if (WIN32)
    # Link DirectInput on Windows
    target_link_libraries(f35_flightsim dinput8 dxguid)
elseif(UNIX AND NOT APPLE)
    # Link GPIO libraries for Raspberry Pi (use one depending on what you're using)
    find_library(PIGPIO_LIB pigpio)
    find_library(PTHREAD_LIB pthread)
    target_link_libraries(f35_flightsim ${PIGPIO_LIB} ${PTHREAD_LIB})
endif()
