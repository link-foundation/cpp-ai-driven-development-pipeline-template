# Resolution of the developer dependencies (GoogleTest, Google Benchmark).
#
# Every package manager the template supports is tried first, so the same
# CMakeLists.txt works unchanged with Conan (CMakeDeps), vcpkg (manifest
# mode), system packages (apt install libgtest-dev) and a bare checkout. Only
# when nothing provides the package, and MY_PACKAGE_FETCH_DEPENDENCIES is ON,
# is a pinned, hash-verified source archive downloaded with FetchContent.

include_guard(GLOBAL)

include(FetchContent)

set(MY_PACKAGE_GTEST_VERSION 1.18.0)
set(MY_PACKAGE_GTEST_SHA256 6e3191c1455468b3fc35a417fb565c1c5071aee1b7e7f85e30cf48a98d37d8b5)
set(MY_PACKAGE_BENCHMARK_VERSION 1.9.5)
set(MY_PACKAGE_BENCHMARK_SHA256 9631341c82bac4a288bef951f8b26b41f69021794184ece969f8473977eaa340)

macro(my_package_require_gtest)
    if(NOT TARGET GTest::gtest_main)
        find_package(GTest QUIET)
    endif()
    if(NOT TARGET GTest::gtest_main)
        if(NOT MY_PACKAGE_FETCH_DEPENDENCIES)
            message(FATAL_ERROR "GoogleTest was not found and MY_PACKAGE_FETCH_DEPENDENCIES is OFF. "
                                "Install it with Conan, vcpkg or your system package manager."
            )
        endif()
        message(STATUS "GoogleTest not found, fetching v${MY_PACKAGE_GTEST_VERSION}")
        # Link against the same CRT as the tests on MSVC.
        set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
        set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
        set(BUILD_GMOCK OFF CACHE BOOL "" FORCE)
        FetchContent_Declare(
            googletest
            URL "https://github.com/google/googletest/archive/refs/tags/v${MY_PACKAGE_GTEST_VERSION}.tar.gz"
            URL_HASH "SHA256=${MY_PACKAGE_GTEST_SHA256}"
            DOWNLOAD_EXTRACT_TIMESTAMP ON
            SYSTEM
        )
        FetchContent_MakeAvailable(googletest)
    endif()
endmacro()

macro(my_package_require_benchmark)
    if(NOT TARGET benchmark::benchmark)
        find_package(benchmark QUIET)
    endif()
    if(NOT TARGET benchmark::benchmark)
        if(NOT MY_PACKAGE_FETCH_DEPENDENCIES)
            message(FATAL_ERROR "Google Benchmark was not found and MY_PACKAGE_FETCH_DEPENDENCIES is OFF.")
        endif()
        message(STATUS "Google Benchmark not found, fetching v${MY_PACKAGE_BENCHMARK_VERSION}")
        set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
        set(BENCHMARK_ENABLE_GTEST_TESTS OFF CACHE BOOL "" FORCE)
        set(BENCHMARK_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
        FetchContent_Declare(
            benchmark
            URL "https://github.com/google/benchmark/archive/refs/tags/v${MY_PACKAGE_BENCHMARK_VERSION}.tar.gz"
            URL_HASH "SHA256=${MY_PACKAGE_BENCHMARK_SHA256}"
            DOWNLOAD_EXTRACT_TIMESTAMP ON
            SYSTEM
        )
        FetchContent_MakeAvailable(benchmark)
    endif()
endmacro()
