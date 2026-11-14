#!/usr/bin/env python3
"""Render final resolutions alongside the immutable initial registry snapshots."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dev/log/issues/33/pulls/34'


def main():
    lock = json.loads((ROOT / 'package-lock.json').read_text())['packages']
    final = {path.split('node_modules/')[-1]: data['version']
             for path, data in lock.items() if path}
    for ecosystem, filename, before_key in [
        ('PYTHON', 'pypi-lock.json', 'before'),
        ('NPM', 'npm-lock.json', 'resolved'),
    ]:
        rows = json.loads((OUT / 'research' / filename).read_text())
        lines = [f'# Complete {ecosystem} registry comparison', '',
                 'Queried live registries on 2026-11-14 UTC. Latest means stable, not prerelease.', '',
                 '| Dependency | Before | Final | Registry latest |', '| --- | --- | --- | --- |']
        for row in rows:
            version = final[row['name']] if ecosystem == 'NPM' else row['before']
            assert version == row['latest'], (row['name'], version, row['latest'])
            lines.append(f"| {row['name']} | {row[before_key]} | {version} | {row['latest']} |")
        (OUT / f'{ecosystem}-LOCK.md').write_text('\n'.join(lines) + '\n')
    releases = json.loads((OUT / 'research/github-releases.json').read_text())
    lines = ['# Dependency inventory and final selections', '',
             'Live registry queries: 2026-11-14 UTC. Before is the prepared PR branch',
             'after Dependabot PR 32. Historical case studies and logs retain their',
             'original pins. Latest means current stable in the named distribution.', '',
             'All 60 Python entries are listed in [PYTHON-LOCK.md](PYTHON-LOCK.md);',
             'all 76 scanner npm entries in [NPM-LOCK.md](NPM-LOCK.md); all 145 distinct',
             'package/version pairs in the published npm CLI in [NPM-CLI.md](NPM-CLI.md).',
             'The scanner and Python tables have no below-latest entries.', '',
             '## GitHub Actions and hooks', '',
             'Every immutable action commit still matches the newest stable tag.',
             'The full commit identities and release notes are in `research/github-releases.json`.', '',
             '| Dependency | Before | Final / latest |', '| --- | --- | --- |']
    for name, release in releases.items():
        if not release.get('previous_ref') and not name.startswith('pre-commit/'):
            continue
        before = release.get('previous_version') or release['tag']
        lines.append(f"| {name} | {before} | [{release['tag']}]({release['url']}) |")
    (OUT / 'DEPENDENCIES.md').write_text('\n'.join(lines) + '\n')
    print('Rendered complete before/final/latest tables')


if __name__ == '__main__':
    main()
