#!/usr/bin/env bash
# Consume an installed copy through pkg-config, without CMake:
#   PKG_CONFIG_PATH=/path/to/install/prefix/share/pkgconfig ./build.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
out_dir="${1:-build}"
mkdir -p "$out_dir"
# shellcheck disable=SC2046 # word splitting of the flags is intended
"${CXX:-c++}" -std=c++20 $(pkg-config --cflags my_package) ../main.cpp -o "$out_dir/consumer"
"$out_dir/consumer"
echo "pkg-config consumer: OK"
