#!/usr/bin/env python3
"""Save a fresh registry inventory for issue 33 without executing dependencies."""
import importlib.util
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dev/log/issues/33/pulls/34'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'experiments' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True))


def main():
    raw = OUT / 'research'
    direct = load('direct', 'research_issue_30_dependencies.py')
    direct.OUT = raw
    direct.main()
    previous = dict(re.findall(r'^([\w-]+)==([^\s;]+)',
                              (ROOT / 'scripts/constraints.txt').read_text(), re.M))
    records = []
    for name, version in previous.items():
        with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json') as response:
            info = json.load(response)['info']
        records.append({'name': name, 'before': version, 'latest': info['version'],
                        'requires_dist': info['requires_dist'],
                        'requires_python': info['requires_python']})
    (raw / 'pypi-lock.json').write_text(json.dumps(records, indent=2) + '\n')
    npm = load('npm', 'research_issue_30_npm.py')
    npm.OUT = OUT
    (OUT / 'raw').mkdir(exist_ok=True)
    npm.main()
    (OUT / 'raw/npm-lock.json').replace(raw / 'npm-lock.json')
    (OUT / 'raw').rmdir()
    # The reused collector describes issue 30's absent lock. Correct issue 33's
    # baseline: every current lock entry already existed at the start of work.
    npm_rows = json.loads((raw / 'npm-lock.json').read_text())
    for ecosystem, rows, version_key in [('PYTHON', records, 'before'), ('NPM', npm_rows, 'resolved')]:
        lines = [f'# Complete {ecosystem} registry comparison', '',
                 'Queried live registries on 2026-11-14 UTC. Latest means stable, not prerelease.', '',
                 '| Dependency | Before | Registry latest |', '| --- | --- | --- |']
        for row in rows:
            lines.append(f"| {row['name']} | {row[version_key]} | {row['latest']} |")
        (OUT / f'{ecosystem}-LOCK.md').write_text('\n'.join(lines) + '\n')
        print(ecosystem, 'mismatches:', [(r['name'], r[version_key], r['latest']) for r in rows if r[version_key] != r['latest']], flush=True)
    with urllib.request.urlopen('https://nodejs.org/dist/index.json') as response:
        nodes = json.load(response)
    (raw / 'node-releases.json').write_text(json.dumps(nodes[:5], indent=2) + '\n')
    with urllib.request.urlopen('https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json') as response:
        index = json.load(response)
    (raw / 'dotnet-index.json').write_text(json.dumps(index, indent=2) + '\n')
    (raw / 'vcpkg-head.json').write_text(json.dumps(api('repos/microsoft/vcpkg/commits/master'), indent=2) + '\n')
    print('Inventory complete', flush=True)


if __name__ == '__main__':
    main()
