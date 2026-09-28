# Consume an installed copy: `cmake --install`, the release "headers" archive,
# a Conan package (CMakeDeps) or a vcpkg port all provide this package config.
#
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/install/prefix
cmake_minimum_required(VERSION 3.21)
project(my_package_find_package_consumer LANGUAGES CXX)

find_package(my_package CONFIG REQUIRED)

add_executable(consumer ../main.cpp)
target_link_libraries(consumer PRIVATE my_package::my_package)

enable_testing()
add_test(NAME consumer COMMAND consumer)
