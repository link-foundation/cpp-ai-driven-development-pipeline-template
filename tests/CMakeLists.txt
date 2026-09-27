my_package_require_gtest()

add_executable(${PROJECT_NAME}_tests my_package_tests.cpp)
target_link_libraries(${PROJECT_NAME}_tests PRIVATE ${PROJECT_NAME}::${PROJECT_NAME} GTest::gtest_main)
my_package_apply_project_options(${PROJECT_NAME}_tests)

include(GoogleTest)
gtest_discover_tests(${PROJECT_NAME}_tests DISCOVERY_TIMEOUT 60 PROPERTIES TIMEOUT 60)
