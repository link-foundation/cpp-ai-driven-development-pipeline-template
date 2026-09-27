// Minimal program that uses my_package. Built by CI to prove the public
// headers compile on every supported compiler.

#include <my_package/my_package.hpp>

#include <cstdlib>
#include <exception>
#include <iostream>

namespace
{
    auto run() -> int
    {
        std::cout << "add(2, 3) = " << my_package::add(2, 3) << '\n';
        std::cout << "multiply(6, 7) = " << my_package::multiply(6, 7) << '\n';
        std::cout << "fibonacci(50) = " << my_package::fibonacci(50) << '\n';

        const auto parsed = my_package::parse_unsigned("2026");
        if (!parsed.has_value())
        {
            std::cerr << "parse_unsigned failed\n";
            return EXIT_FAILURE;
        }
        std::cout << "parse_unsigned(\"2026\") = " << *parsed << '\n';
        return EXIT_SUCCESS;
    }
} // namespace

auto main() -> int
{
    try
    {
        return run();
    }
    catch (const std::exception& error)
    {
        std::cerr << "error: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
