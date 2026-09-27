# Consume the repository itself as the distributable, pinned to a release tag.
#
# CI replaces the download with the local checkout through the standard
# FetchContent override:
#   cmake -S . -B build -DFETCHCONTENT_SOURCE_DIR_MY_PACKAGE=/path/to/checkout
cmake_minimum_required(VERSION 3.24)
project(my_package_fetch_content_consumer LANGUAGES CXX)

include(FetchContent)
FetchContent_Declare(
    my_package
    GIT_REPOSITORY https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template.git
    GIT_TAG v0.1.0
    GIT_SHALLOW TRUE
    # Prefer an installed copy (Conan, vcpkg, system) when one exists.
    FIND_PACKAGE_ARGS CONFIG
)
FetchContent_MakeAvailable(my_package)

add_executable(consumer ../main.cpp)
target_link_libraries(consumer PRIVATE my_package::my_package)

enable_testing()
add_test(NAME consumer COMMAND consumer)
