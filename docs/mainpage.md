# my_package API reference {#mainpage}

`my_package` is the example header-only C++20 library of the
[C++ AI-driven development pipeline template](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template).
Every public symbol lives in the `my_package` namespace and is declared in
`<my_package/my_package.hpp>`; this reference is generated from those headers
by Doxygen on every push to `main`.

## Using the library

```cpp
#include <my_package/my_package.hpp>

static_assert(my_package::add(2, 3) == 5);
static_assert(my_package::fibonacci(10) == 55);
```

The complete example program is @ref basic_usage.cpp.

## Getting the package

The same sources are published through every C/C++ distribution channel:

| Channel | How to consume |
| --- | --- |
| The repository itself | `add_subdirectory`, git submodule, `FetchContent`, CPM.cmake |
| GitHub release | source archive, install tree, vcpkg overlay port, `SHA256SUMS` |
| CMake package | `find_package(my_package CONFIG REQUIRED)` after `cmake --install` |
| pkg-config | `pkg-config --cflags my_package` |
| vcpkg | the overlay port attached to each release, or a registry |
| Conan 2 | `conan create .`, or a Conan remote |
| NuGet | the native package for MSBuild/Visual Studio projects |

See the repository README for step-by-step instructions.

@example basic_usage.cpp
Prints the result of every function of the library.
