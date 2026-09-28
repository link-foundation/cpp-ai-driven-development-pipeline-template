// Shared by every consumer example: proves that a project which only knows the
// public interface of my_package can compile and link against it.

#include <my_package/my_package.hpp>

#include <cstdlib>

auto main() -> int
{
    // cppcheck-suppress knownConditionTrueFalse ; the point is to call the linked library at run time
    return my_package::add(2, 3) == 5 ? EXIT_SUCCESS : EXIT_FAILURE;
}
