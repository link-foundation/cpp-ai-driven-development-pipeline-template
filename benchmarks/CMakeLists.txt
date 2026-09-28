my_package_require_benchmark()

add_executable(${PROJECT_NAME}_benchmarks my_package_benchmarks.cpp)
target_link_libraries(${PROJECT_NAME}_benchmarks PRIVATE ${PROJECT_NAME}::${PROJECT_NAME} benchmark::benchmark_main)
my_package_apply_project_options(${PROJECT_NAME}_benchmarks)
