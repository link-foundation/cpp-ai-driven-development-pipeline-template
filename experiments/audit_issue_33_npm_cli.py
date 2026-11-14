#!/usr/bin/env python3
"""Inventory/audit the published npm CLI bundle without rewriting its packages."""
import concurrent.futures
import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dev/log/issues/33/pulls/34'
CLI = ROOT / '.tools/npm-cli/lib/node_modules/npm'
NPM = ['node', str(CLI / 'bin/npm-cli.js')]


def latest(name):
    with urllib.request.urlopen('https://registry.npmjs.org/' + urllib.parse.quote(name, safe='') + '/latest') as response:
        data = json.load(response)
    return name, data['version']


def main():
    packages = set()
    for directory, subdirs, files in os.walk(CLI):
        subdirs[:] = [d for d in subdirs if not d.startswith('.')]
        if 'package.json' not in files:
            continue
        # Only package roots, not fixture/example manifests within packages.
        path = Path(directory)
        if path != CLI and path.parent.name != 'node_modules' and not path.parent.name.startswith('@'):
            continue
        package = json.loads((path / 'package.json').read_text())
        if package.get('name') and package.get('version'):
            packages.add((package['name'], package['version']))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        registry = dict(pool.map(latest, sorted({name for name, _ in packages})))
    records = [{'name': name, 'before': version, 'resolved': version, 'latest': registry[name]}
               for name, version in sorted(packages)]
    (OUT / 'research/npm-cli-tree.json').write_text(json.dumps(records, indent=2) + '\n')
    lines = ['# npm CLI distribution dependencies', '',
             'Live npm registry comparison of the published npm 12.2.2 bundle. Before and',
             'resolved are identical: this PR retains the current published CLI. Its bundle',
             'is controlled upstream; application overrides cannot change these copies.',
             'Every below-latest entry has this distribution constraint, tracked in npm/cli#10299.', '',
             '| Dependency | Before / resolved | Registry latest |', '| --- | --- | --- |']
    lines += [f"| {r['name']} | {r['resolved']} | {r['latest']} |" for r in records]
    (OUT / 'NPM-CLI.md').write_text('\n'.join(lines) + '\n')
    scratch = ROOT / 'build/npm-cli-audit'
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / 'package.json').write_text(json.dumps({'private': True, 'dependencies': {'npm': '12.2.2'}}) + '\n')
    with (OUT / 'research/npm-cli-audit-install.log').open('w') as log:
        subprocess.run([*NPM, 'install', '--package-lock-only', '--ignore-scripts',
                        '--registry=https://registry.npmjs.org'],
                       cwd=scratch, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = subprocess.run([*NPM, 'audit', '--package-lock-only', '--json',
                             '--registry=https://registry.npmjs.org'],
                            cwd=scratch, capture_output=True, text=True)
    (OUT / 'research/npm-cli-audit.json').write_text(result.stdout)
    (OUT / 'research/npm-cli-audit-stderr.txt').write_text(result.stderr)
    report = json.loads(result.stdout)
    if 'error' in report or 'metadata' not in report:
        raise RuntimeError('npm CLI audit did not complete; inspect the saved report')
    print('CLI packages:', len(records), 'audit:', report.get('metadata', {}).get('vulnerabilities'), flush=True)


if __name__ == '__main__':
    main()
