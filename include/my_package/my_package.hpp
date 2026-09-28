/// @file my_package.hpp
/// @brief Public entry point of the `my_package` example library.
///
/// This header is intentionally tiny: it exists so that every stage of the
/// CI/CD pipeline (build, tests, sanitizers, coverage, Doxygen, packaging for
/// Conan, vcpkg, NuGet and the CMake package config) has real code to work
/// with. Replace it with your own library when you use the template.

#ifndef MY_PACKAGE_MY_PACKAGE_HPP
#define MY_PACKAGE_MY_PACKAGE_HPP

#include <concepts>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string_view>

/// @brief Everything provided by the example library.
namespace my_package
{
    /// @brief Any built-in integer or floating-point type except `bool`.
    template <typename T>
    concept Arithmetic = (std::integral<T> || std::floating_point<T>) && !std::same_as<T, bool>;

    /// @brief Adds two numbers.
    ///
    /// @tparam T An arithmetic type.
    /// @param left The first addend.
    /// @param right The second addend.
    /// @return The sum of @p left and @p right.
    ///
    /// @code
    /// static_assert(my_package::add(2, 3) == 5);
    /// @endcode
    template <Arithmetic T>
    [[nodiscard]] constexpr auto add(T left, T right) noexcept -> T
    {
        return left + right;
    }

    /// @brief Multiplies two numbers.
    ///
    /// @tparam T An arithmetic type.
    /// @param left The multiplicand.
    /// @param right The multiplier.
    /// @return The product of @p left and @p right.
    template <Arithmetic T>
    [[nodiscard]] constexpr auto multiply(T left, T right) noexcept -> T
    {
        return left * right;
    }

    /// @brief Computes the n-th Fibonacci number.
    ///
    /// The sequence starts with `fibonacci(0) == 0` and `fibonacci(1) == 1`.
    ///
    /// @param index Zero-based position in the sequence.
    /// @return The Fibonacci number at @p index.
    /// @throws std::overflow_error If the result does not fit into `std::uint64_t`
    ///         (that is, when @p index is greater than 93).
    [[nodiscard]] constexpr auto fibonacci(std::uint32_t index) -> std::uint64_t
    {
        constexpr std::uint32_t max_index = 93;
        if (index > max_index)
        {
            throw std::overflow_error("my_package::fibonacci: result does not fit into std::uint64_t");
        }
        std::uint64_t previous = 0;
        std::uint64_t current = 1;
        for (std::uint32_t step = 0; step < index; ++step)
        {
            const std::uint64_t next = previous + current;
            previous = current;
            current = next;
        }
        return previous;
    }

    /// @brief Parses a non-negative decimal integer.
    ///
    /// Unlike `std::stoull`, the function never throws: any input that is not
    /// a complete, in-range decimal number yields `std::nullopt`.
    ///
    /// @param text The characters to parse, without sign or whitespace.
    /// @return The parsed value, or `std::nullopt` if @p text is not a valid number.
    [[nodiscard]] constexpr auto parse_unsigned(std::string_view text) noexcept -> std::optional<std::uint64_t>
    {
        if (text.empty())
        {
            return std::nullopt;
        }
        constexpr std::uint64_t radix = 10;
        constexpr std::uint64_t limit = std::numeric_limits<std::uint64_t>::max();
        std::uint64_t value = 0;
        for (const char symbol : text)
        {
            if (symbol < '0' || symbol > '9')
            {
                return std::nullopt;
            }
            const auto digit = static_cast<std::uint64_t>(symbol - '0');
            if (value > (limit - digit) / radix)
            {
                return std::nullopt;
            }
            value = (value * radix) + digit;
        }
        return value;
    }
} // namespace my_package

#endif // MY_PACKAGE_MY_PACKAGE_HPP
