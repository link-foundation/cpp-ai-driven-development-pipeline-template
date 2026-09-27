cmake_minimum_required(VERSION 3.21)
project(test_package LANGUAGES CXX)

find_package(my_package CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE my_package::my_package)
target_compile_features(test_package PRIVATE cxx_std_20)
