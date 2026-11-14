#!/usr/bin/env python3
"""Run the pinned CMake action with deprecation tracing, outside a hosted runner."""

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_workflow_regression():
    spec = importlib.util.spec_from_file_location(
        'dependency_tests', ROOT / 'scripts/tests/test_dependency_pins.py'
    )
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    with tempfile.TemporaryDirectory(prefix='issue-30-cmake-') as directory:
        baseline = Path(directory)
        (baseline / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/requirements-toolchain.txt',
                        baseline / 'scripts/requirements-toolchain.txt')
        workflow = baseline / '.github/workflows/security.yml'
        workflow.parent.mkdir(parents=True)
        workflow.write_bytes(subprocess.check_output([
            'git', 'show', '474a0f0a709ef94f7364d31968c8142d527a9a89:.github/workflows/security.yml',
        ], cwd=ROOT))
        tests.ROOT = baseline
        try:
            tests.test_cmake_action_uses_consistent_cmake_and_ninja_pins()
        except AssertionError:
            print('PASS: regression rejects the deprecated-toolkit action')
        else:
            raise AssertionError('Regression must reject the previous action')
    tests.ROOT = ROOT
    tests.test_cmake_action_uses_consistent_cmake_and_ninja_pins()
    print('PASS: all ten modern action steps retain explicit CMake/Ninja pins')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default='node')
    parser.add_argument('--policy-only', action='store_true')
    args = parser.parse_args()
    check_workflow_regression()
    if args.policy_only:
        return
    scratch = ROOT / 'build/cmake-action-smoke'
    scratch.mkdir(parents=True, exist_ok=True)
    ref = re.search(r'lukka/get-cmake@([0-9a-f]{40})',
                    (ROOT / '.github/workflows/security.yml').read_text()).group(1)
    bundle = scratch / 'index.js'
    if not bundle.exists():
        with bundle.open('wb') as output:
            subprocess.run([
                'gh', 'api', f'repos/lukka/get-cmake/contents/dist/index.js?ref={ref}',
                '-H', 'Accept: application/vnd.github.raw+json',
            ], stdout=output, check=True)
    for name in ('path', 'output'):
        (scratch / name).write_text('')
    (scratch / 'tmp').mkdir(exist_ok=True)
    env = {**os.environ, 'INPUT_CMAKEVERSION': '4.5.0', 'INPUT_NINJAVERSION': '1.13.2',
           'INPUT_USECLOUDCACHE': 'false', 'INPUT_USELOCALCACHE': 'false',
           'RUNNER_OS': 'Linux', 'RUNNER_ARCH': 'X64',
           'RUNNER_TEMP': str(scratch / 'tmp'), 'GITHUB_WORKSPACE': str(ROOT),
           'GITHUB_ACTIONS': 'true', 'GITHUB_PATH': str(scratch / 'path'),
           'GITHUB_OUTPUT': str(scratch / 'output')}
    log = ROOT / 'dev/log/issues/30/pulls/31/raw/get-cmake-smoke.log'
    with log.open('w') as output:
        subprocess.run([args.node, '--max-old-space-size=256', '--trace-deprecation',
                        str(bundle)], env=env, stdout=output,
                       stderr=subprocess.STDOUT, check=True)
    assert 'DeprecationWarning' not in log.read_text()
    paths = os.pathsep.join((scratch / 'path').read_text().splitlines())
    for tool, version in (('cmake', '4.5.0'), ('ninja', '1.13.2')):
        binary = shutil.which(tool, path=paths)
        assert binary, tool
        actual = subprocess.check_output([binary, '--version'], text=True)
        assert version in actual, actual
        print(actual.splitlines()[0])
    print('PASS: checksum-verified CMake/Ninja action, no deprecation warning')


if __name__ == '__main__':
    main()
