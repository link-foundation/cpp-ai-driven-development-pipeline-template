#!/usr/bin/env bash
# Validate the stdlib-built native .nupkg with the real NuGet client: push it
# to a local folder feed and let `dotnet restore` extract it via
# <PackageDownload> (which skips the TFM compatibility check that a native
# package would fail in an SDK-style project).
# Usage: experiments/nuget_package_restore.sh   (needs the dotnet SDK)
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cd "$repo_root"
python3 scripts/pack_nuget.py --out-dir "$work/dist" > "$work/pack.log"
id="$(sed -n 's/^Output: id=//p' "$work/pack.log")"
version="$(sed -n 's/^Output: version=//p' "$work/pack.log")"
mkdir -p "$work/feed" "$work/project"
dotnet nuget push "$work/dist/$id.$version.nupkg" --source "$work/feed"
cat > "$work/project/check.csproj" <<XML
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><TargetFramework>netstandard2.0</TargetFramework><DisableImplicitNuGetFallbackFolder>true</DisableImplicitNuGetFallbackFolder><DisableImplicitFrameworkReferences>true</DisableImplicitFrameworkReferences></PropertyGroup>
  <ItemGroup><PackageDownload Include="$id" Version="[$version]" /></ItemGroup>
</Project>
XML
cat > "$work/project/nuget.config" <<XML
<configuration><packageSources><clear /><add key="local" value="$work/feed" /></packageSources></configuration>
XML
dotnet restore "$work/project/check.csproj" --packages "$work/packages"
extracted="$work/packages/$(echo "$id" | tr '[:upper:]' '[:lower:]')/$version"
test -f "$extracted/build/native/$id.targets"
find "$extracted/lib/native/include" -type f | grep -q .
echo "NuGet restore of $id $version: OK"
