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
    BENCHMARK(fibonacci_benchmark)->Arg(10)->Arg(50)->Arg(93);

    void parse_unsigned_benchmark(benchmark::State& state)
    {
        for ([[maybe_unused]] auto _ : state)
        {
            benchmark::DoNotOptimize(my_package::parse_unsigned("18446744073709551615"));
        }
    }
    BENCHMARK(parse_unsigned_benchmark);
} // namespace
