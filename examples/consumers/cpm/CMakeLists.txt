# Consume the repository through CPM.cmake (https://github.com/cpm-cmake/CPM.cmake).
#
# CI replaces the download with the local checkout through CPM's override:
#   cmake -S . -B build -DCPM_my_package_SOURCE=/path/to/checkout
cmake_minimum_required(VERSION 3.21)
project(my_package_cpm_consumer LANGUAGES CXX)

set(CPM_VERSION 0.42.0)
set(CPM_SHA256 2020b4fc42dba44817983e06342e682ecfc3d2f484a581f11cc5731fbe4dce8a)
set(CPM_FILE "${CMAKE_BINARY_DIR}/cmake/CPM_${CPM_VERSION}.cmake")
if(NOT EXISTS "${CPM_FILE}")
    file(DOWNLOAD "https://github.com/cpm-cmake/CPM.cmake/releases/download/v${CPM_VERSION}/CPM.cmake" "${CPM_FILE}"
         EXPECTED_HASH SHA256=${CPM_SHA256}
    )
endif()
include("${CPM_FILE}")

CPMAddPackage(
    NAME my_package
    GITHUB_REPOSITORY link-foundation/cpp-ai-driven-development-pipeline-template
    VERSION 0.1.0
    GIT_TAG v0.1.0
)

add_executable(consumer ../main.cpp)
target_link_libraries(consumer PRIVATE my_package::my_package)

enable_testing()
add_test(NAME consumer COMMAND consumer)
