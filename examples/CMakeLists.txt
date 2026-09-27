add_executable(${PROJECT_NAME}_basic_usage basic_usage.cpp)
target_link_libraries(${PROJECT_NAME}_basic_usage PRIVATE ${PROJECT_NAME}::${PROJECT_NAME})
my_package_apply_project_options(${PROJECT_NAME}_basic_usage)

if(MY_PACKAGE_BUILD_TESTS)
    add_test(NAME ${PROJECT_NAME}_basic_usage COMMAND ${PROJECT_NAME}_basic_usage)
endif()
