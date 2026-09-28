# Consume a vendored copy or a git submodule:
#   git submodule add https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template.git external/my_package
#   cmake -S . -B build -DMY_PACKAGE_DIR=external/my_package
cmake_minimum_required(VERSION 3.21)
project(my_package_add_subdirectory_consumer LANGUAGES CXX)

set(MY_PACKAGE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/my_package" CACHE PATH "Path to the my_package sources")
add_subdirectory("${MY_PACKAGE_DIR}" my_package EXCLUDE_FROM_ALL)

add_executable(consumer ../main.cpp)
target_link_libraries(consumer PRIVATE my_package::my_package)

enable_testing()
add_test(NAME consumer COMMAND consumer)
