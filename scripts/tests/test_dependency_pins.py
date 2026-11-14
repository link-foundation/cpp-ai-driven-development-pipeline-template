"""A fresh install must use the committed versions on every supported platform."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def pins(text):
    return dict(re.findall(r'^([\w-]+)==([^\s;]+)', text, re.M))


def test_generated_manifests_use_the_shared_resolution():
    scripts = ROOT / 'scripts'
    locked = pins((scripts / 'constraints.txt').read_text())
    assert locked
    for group in ('ci', 'security', 'toolchain'):
        source = pins((scripts / f'requirements-{group}.in').read_text())
        manifest = (scripts / f'requirements-{group}.txt').read_text()
        assert '-c constraints.txt' in manifest
        assert pins(manifest) == source
        assert all(locked.get(name) == version for name, version in source.items())


def test_hook_formatter_matches_ci():
    ci = pins((ROOT / 'scripts/requirements-ci.txt').read_text())
    hooks = (ROOT / '.pre-commit-config.yaml').read_text()
    formatter = hooks.split('repo: https://github.com/pre-commit/mirrors-clang-format', 1)[1]
    assert re.search(r'rev: v' + re.escape(ci['clang-format']) + r'\b', formatter)


def test_every_python_job_uses_the_declared_stable_version():
    version = (ROOT / '.python-version').read_text().strip()
    for workflow in (ROOT / '.github/workflows').glob('*.yml'):
        for pin in re.findall(r"python-version: '([^']+)'", workflow.read_text()):
            assert pin == version, workflow.name


def test_vcpkg_overlay_matches_fetchcontent_benchmark():
    import json

    manifest = json.loads((ROOT / "packaging/vcpkg-overlays/benchmark/vcpkg.json").read_text())
    cmake = (ROOT / "cmake/Dependencies.cmake").read_text()
    version = re.search(r'set\(MY_PACKAGE_BENCHMARK_VERSION ([^\s)]+)', cmake).group(1)
    assert manifest["version-semver"] == version
    config = json.loads((ROOT / "vcpkg-configuration.json").read_text())
    assert "packaging/vcpkg-overlays" in config["overlay-ports"]


def test_benchmark_overlay_forwards_feature_options(tmp_path):
    """Exercise the port/configure boundary without downloading or compiling C++."""
    import shutil
    import subprocess

    import pytest

    cmake = shutil.which('cmake')
    if cmake is None:
        pytest.skip('CMake is required to exercise the vcpkg port')
    port = ROOT / 'packaging/vcpkg-overlays/benchmark/portfile.cmake'
    output = tmp_path / 'options.txt'
    probe = tmp_path / 'probe.cmake'
    # Stub the upstream download/feature APIs and capture the configure call.
    # return() in the configure macro stops the port before build/install steps.
    probe.write_text('''
function(vcpkg_from_github)
endfunction()
function(vcpkg_check_features)
    set(FEATURE_OPTIONS "-DBENCHMARK_INSTALL_TOOLS=${TOOLS}" PARENT_SCOPE)
endfunction()
macro(vcpkg_cmake_configure)
    file(WRITE "${OUTPUT}" "${ARGV}")
    return()
endmacro()
include("${PORT}")
''')
    for features, enabled in (('core', 'OFF'), ('core;tools', 'ON')):
        subprocess.run([
            cmake, f'-DFEATURES={features}', f'-DTOOLS={enabled}',
            f'-DOUTPUT={output}', f'-DPORT={port}', '-P', str(probe),
        ], check=True, capture_output=True, text=True)
        options = output.read_text().split(';')
        assert f'-DBENCHMARK_INSTALL_TOOLS={enabled}' in options
        assert 'core' not in options
        assert 'tools' not in options
