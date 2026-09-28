# `<project>_docs` target: runs Doxygen with the repository Doxyfile, exactly
# like the CI docs job, so `cmake --build <dir> --target my_package_docs`
# reproduces the published API reference in docs/api/ locally.
find_package(Doxygen QUIET)
if(NOT DOXYGEN_FOUND)
    message(STATUS "Doxygen not found: the ${PROJECT_NAME}_docs target is not available")
    return()
endif()

add_custom_target(
    ${PROJECT_NAME}_docs
    COMMAND "${CMAKE_COMMAND}" -E env "DOXYGEN_PROJECT_NUMBER=${PROJECT_VERSION}" "${DOXYGEN_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    COMMENT "Generating the API reference in docs/api/ with Doxygen"
    VERBATIM
)
