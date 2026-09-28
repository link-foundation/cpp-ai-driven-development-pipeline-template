#include <my_package/my_package.hpp>

#include <gtest/gtest.h>

#include <cstdint>
#include <limits>
#include <stdexcept>

namespace
{
    // Compile-time checks: the whole API is constexpr.
    static_assert(my_package::add(2, 3) == 5);
    static_assert(my_package::multiply(4, 5) == 20);
    static_assert(my_package::fibonacci(10) == 55);
    static_assert(my_package::parse_unsigned("42") == 42U);
    static_assert(!my_package::parse_unsigned("4x2").has_value());

    TEST(AddTest, AddsIntegers)
    {
        EXPECT_EQ(my_package::add(2, 3), 5);
        EXPECT_EQ(my_package::add(-2, 3), 1);
    }

    TEST(AddTest, AddsFloatingPointNumbers)
    {
        EXPECT_DOUBLE_EQ(my_package::add(0.5, 0.25), 0.75);
    }

    TEST(MultiplyTest, MultipliesIntegers)
    {
        EXPECT_EQ(my_package::multiply(6, 7), 42);
        EXPECT_EQ(my_package::multiply(-3, 3), -9);
    }

    TEST(MultiplyTest, MultipliesFloatingPointNumbers)
    {
        EXPECT_DOUBLE_EQ(my_package::multiply(1.5, 4.0), 6.0);
    }

    TEST(FibonacciTest, StartsWithZeroAndOne)
    {
        EXPECT_EQ(my_package::fibonacci(0), 0U);
        EXPECT_EQ(my_package::fibonacci(1), 1U);
        EXPECT_EQ(my_package::fibonacci(2), 1U);
    }

    TEST(FibonacciTest, ComputesLargestRepresentableValue)
    {
        EXPECT_EQ(my_package::fibonacci(93), 12200160415121876738ULL);
    }

    TEST(FibonacciTest, ThrowsOnOverflow)
    {
        EXPECT_THROW(static_cast<void>(my_package::fibonacci(94)), std::overflow_error);
    }

    TEST(ParseUnsignedTest, ParsesValidNumbers)
    {
        EXPECT_EQ(my_package::parse_unsigned("0"), 0U);
        EXPECT_EQ(my_package::parse_unsigned("18446744073709551615"), std::numeric_limits<std::uint64_t>::max());
    }

    TEST(ParseUnsignedTest, RejectsInvalidInput)
    {
        EXPECT_FALSE(my_package::parse_unsigned("").has_value());
        EXPECT_FALSE(my_package::parse_unsigned("-1").has_value());
        EXPECT_FALSE(my_package::parse_unsigned(" 1").has_value());
        EXPECT_FALSE(my_package::parse_unsigned("18446744073709551616").has_value());
    }
} // namespace
