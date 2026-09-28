# Install rules, CMake package config and pkg-config file.
#
# After `cmake --install`, consumers can use either
#   find_package(my_package CONFIG REQUIRED)
#   target_link_libraries(app PRIVATE my_package::my_package)
# or
#   pkg-config --cflags my_package
# The same install tree is what the Conan recipe, the vcpkg port and the
# release "headers" archive package, so all channels expose identical files.

include_guard(GLOBAL)

include(CMakePackageConfigHelpers)

# A header-only library is architecture independent, so its package config
# lives under share/ where every architecture's find_package() looks.
set(MY_PACKAGE_INSTALL_CMAKEDIR
    "${CMAKE_INSTALL_DATADIR}/cmake/${PROJECT_NAME}"
    CACHE STRING "Install directory of the CMake package config files"
)
set(MY_PACKAGE_INSTALL_PKGCONFIGDIR
    "${CMAKE_INSTALL_DATADIR}/pkgconfig"
    CACHE STRING "Install directory of the pkg-config file"
)

install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets)

install(
    DIRECTORY "${PROJECT_SOURCE_DIR}/include/"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    FILES_MATCHING
    PATTERN "*.h"
    PATTERN "*.hpp"
)

install(
    EXPORT ${PROJECT_NAME}Targets
    NAMESPACE ${PROJECT_NAME}::
    DESTINATION "${MY_PACKAGE_INSTALL_CMAKEDIR}"
)

configure_package_config_file(
    "${PROJECT_SOURCE_DIR}/cmake/PackageConfig.cmake.in" "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    INSTALL_DESTINATION "${MY_PACKAGE_INSTALL_CMAKEDIR}"
)

write_basic_package_version_file(
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
    ARCH_INDEPENDENT
)

install(FILES "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
              "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake"
        DESTINATION "${MY_PACKAGE_INSTALL_CMAKEDIR}"
)

configure_file("${PROJECT_SOURCE_DIR}/cmake/package.pc.in" "${PROJECT_BINARY_DIR}/${PROJECT_NAME}.pc" @ONLY)
install(FILES "${PROJECT_BINARY_DIR}/${PROJECT_NAME}.pc" DESTINATION "${MY_PACKAGE_INSTALL_PKGCONFIGDIR}")

install(FILES "${PROJECT_SOURCE_DIR}/LICENSE" DESTINATION "${CMAKE_INSTALL_DATADIR}/licenses/${PROJECT_NAME}"
        OPTIONAL
)
