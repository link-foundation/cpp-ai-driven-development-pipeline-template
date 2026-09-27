#!/usr/bin/env bash
# Round trip of the release vcpkg port: package the release with a file://
# "GitHub server", then let vcpkg download the source asset through the port,
# verify its SHA512, build, install and consume it with find_package().
# Usage: VCPKG_ROOT=/path/to/vcpkg experiments/vcpkg_release_port_roundtrip.sh
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
: "${VCPKG_ROOT:?set VCPKG_ROOT to a bootstrapped vcpkg checkout}"

cd "$repo_root"
GITHUB_SERVER_URL="file://$work/server" GITHUB_REPOSITORY=owner/repo \
  python3 scripts/package_release.py --out-dir "$work/dist" --skip-install-tree
version="$(python3 scripts/get_version.py | sed -n 's/^Output: version=//p')"
tag="$(python3 scripts/get_version.py | sed -n 's/^Output: tag=//p')"
mkdir -p "$work/server/owner/repo/releases/download/$tag"
cp "$work"/dist/*.tar.gz "$work/server/owner/repo/releases/download/$tag/"
mkdir -p "$work/ports"
tar -xzf "$work"/dist/*-vcpkg-port-"$version".tar.gz -C "$work/ports"
port="$(ls "$work/ports")"

"$VCPKG_ROOT/vcpkg" install "$port" --classic --overlay-ports="$work/ports" \
  --x-install-root="$work/installed" --x-buildtrees-root="$work/buildtrees" \
  --downloads-root="$work/downloads" --binarysource=clear
cmake -S examples/consumers/find_package -B "$work/consumer" \
  -DCMAKE_TOOLCHAIN_FILE="$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_INSTALLED_DIR="$work/installed" -DVCPKG_MANIFEST_MODE=OFF
cmake --build "$work/consumer"
ctest --test-dir "$work/consumer" --output-on-failure
echo "vcpkg release port round trip: OK"
