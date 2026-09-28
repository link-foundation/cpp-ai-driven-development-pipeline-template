#include <my_package/my_package.hpp>

#include <cstdlib>
#include <iostream>

auto main() -> int
{
    constexpr auto value = my_package::fibonacci(10);
    std::cout << "my_package test_package: fibonacci(10) = " << value << '\n';
    return value == 55 ? EXIT_SUCCESS : EXIT_FAILURE;
}
