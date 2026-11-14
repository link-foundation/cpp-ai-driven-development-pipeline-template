#!/usr/bin/env python3
"""Collect release notes for the scanner's explicitly overridden npm majors."""

import concurrent.futures
import json
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dev/log/issues/30/pulls/31/raw'


def release_notes(item):
    name, version = item
    url = 'https://registry.npmjs.org/' + urllib.parse.quote(name, safe='') + '/latest'
    with urllib.request.urlopen(url) as response:
        metadata = json.load(response)
    repository = metadata.get('repository', {})
    repository = repository.get('url', '') if isinstance(repository, dict) else repository
    match = re.search(r'github.com[:/]([^/]+/[^/#]+)', repository)
    result = {'name': name, 'version': version, 'engines': metadata.get('engines'),
              'repository': repository}
    if match:
        slug = match.group(1).removesuffix('.git')
        major = version.split('.')[0]
        for tag in (f'v{major}.0.0', f'{major}.0.0', f'v{version}'):
            process = subprocess.run(
                ['gh', 'api', f'repos/{slug}/releases/tags/{tag}'],
                capture_output=True, text=True, check=False,
            )
            if process.returncode == 0:
                release = json.loads(process.stdout)
                result.update(url=release['html_url'], notes=release.get('body'))
                break
    return result


def main():
    items = json.loads((ROOT / 'package.json').read_text())['overrides'].items()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(release_notes, items))
    (OUT / 'npm-major-migrations.json').write_text(json.dumps(records, indent=2) + '\n')
    for record in records:
        print(record['name'], record['version'], record.get('url', 'NO RELEASE NOTES'))
        print((record.get('notes') or '')[:2500])


if __name__ == '__main__':
    main()
