#!/usr/bin/env python3
"""Verify the copied vcpkg port failed its feature contract before the fix."""

import importlib.util
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location(
        'dependency_tests', ROOT / 'scripts/tests/test_dependency_pins.py'
    )
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    with tempfile.TemporaryDirectory(prefix='issue-30-port-') as directory:
        scratch = Path(directory)
        port = scratch / 'packaging/vcpkg-overlays/benchmark/portfile.cmake'
        port.parent.mkdir(parents=True)
        port.write_bytes(subprocess.check_output([
            'git', 'show',
            '2d96810e569d89e8411fd636203909da63fdf8dd:packaging/vcpkg-overlays/benchmark/portfile.cmake',
        ], cwd=ROOT))
        tests.ROOT = scratch
        try:
            tests.test_benchmark_overlay_forwards_feature_options(scratch)
        except AssertionError:
            print('PASS: regression detects missing CMake feature options in copied port')
        else:
            raise AssertionError('Regression must fail against the copied upstream port')
        tests.ROOT = ROOT
        tests.test_benchmark_overlay_forwards_feature_options(scratch)
        print('PASS: updated port forwards ON/OFF options and omits feature names')


if __name__ == '__main__':
    main()
