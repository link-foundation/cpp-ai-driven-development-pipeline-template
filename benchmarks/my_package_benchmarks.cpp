#include <my_package/my_package.hpp>

#include <benchmark/benchmark.h>

#include <cstdint>

namespace
{
    void fibonacci_benchmark(benchmark::State& state)
    {
        const auto index = static_cast<std::uint32_t>(state.range(0));
        for ([[maybe_unused]] auto _ : state)
        {
            benchmark::DoNotOptimize(my_package::fibonacci(index));
        }
    }
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-non-const-global-variables): the macro registers a global
    BENCHMARK(fibonacci_benchmark)->Arg(10)->Arg(50)->Arg(93);

    // cppcheck-suppress constParameterCallback ; Google Benchmark fixes the callback signature
    void parse_unsigned_benchmark(benchmark::State& state)
    {
        for ([[maybe_unused]] auto _ : state)
        {
            benchmark::DoNotOptimize(my_package::parse_unsigned("18446744073709551615"));
        }
    }
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-non-const-global-variables): the macro registers a global
    BENCHMARK(parse_unsigned_benchmark);
} // namespace
