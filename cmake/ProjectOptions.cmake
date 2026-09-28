# Developer-only build settings: warnings, sanitizers, coverage and CPU tuning.
#
# They are applied to the project's own tests, examples and benchmarks through
# my_package_apply_project_options() and never leak into the library's
# INTERFACE, so consumers are not forced to build with the template's flags.

include_guard(GLOBAL)

function(my_package_apply_project_options target)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /permissive- /utf-8 /Zc:__cplusplus)
        if(MY_PACKAGE_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE /WX)
        endif()
    else()
        target_compile_options(
            ${target}
            PRIVATE -Wall
                    -Wextra
                    -Wpedantic
                    -Wshadow
                    -Wconversion
                    -Wsign-conversion
                    -Wold-style-cast
                    -Wnon-virtual-dtor
                    -Woverloaded-virtual
                    -Wnull-dereference
                    -Wdouble-promotion
        )
        if(MY_PACKAGE_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE -Werror)
        endif()
    endif()

    if(MY_PACKAGE_SANITIZERS)
        list(JOIN MY_PACKAGE_SANITIZERS "," sanitizer_list)
        if(MSVC)
            # MSVC only ships AddressSanitizer.
            if("address" IN_LIST MY_PACKAGE_SANITIZERS)
                target_compile_options(${target} PRIVATE /fsanitize=address)
            endif()
        else()
            target_compile_options(
                ${target} PRIVATE -fsanitize=${sanitizer_list} -fno-omit-frame-pointer -fno-sanitize-recover=all
            )
            target_link_options(${target} PRIVATE -fsanitize=${sanitizer_list})
        endif()
    endif()

    if(MY_PACKAGE_ENABLE_COVERAGE)
        if(MSVC)
            message(WARNING "MY_PACKAGE_ENABLE_COVERAGE is not supported with MSVC; ignoring it")
        else()
            target_compile_options(${target} PRIVATE --coverage -O0 -g)
            target_link_options(${target} PRIVATE --coverage)
        endif()
    endif()

    # linksplatform libraries tune their tests and benchmarks for the host CPU
    # (-march=haswell and friends). Keep it opt-in: -march=native binaries do
    # not run on older CPUs and are not reproducible across runners.
    if(MY_PACKAGE_NATIVE_ARCH AND NOT MSVC)
        target_compile_options(${target} PRIVATE -march=native)
    endif()
endfunction()
