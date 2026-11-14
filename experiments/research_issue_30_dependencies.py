#!/usr/bin/env python3
"""Collect current registry metadata without installing or executing dependencies."""
import json
import re
import subprocess
import urllib.request
from pathlib import Path

OUT = Path('dev/log/issues/30/pulls/31/raw')

def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True))

def main():
    packages = {}
    for path in Path('scripts').glob('requirements-*.txt'):
        packages.update(dict(re.findall(r'^([\w-]+)==([^\s]+)', path.read_text(), re.M)))
    for name in ('pre-commit', 'pip', 'pip-tools', 'uv', 'cmake', 'ninja'):
        packages.setdefault(name, 'not pinned')
    rows = []
    for name, previous in packages.items():
        with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/json') as response:
            data = json.load(response)
        info = data['info']
        row = {'name': name, 'previous': previous, 'latest': info['version'],
               'requires_python': info['requires_python'], 'requires_dist': info['requires_dist'],
               'project_urls': info['project_urls']}
        rows.append(row)
        print(name, previous, '->', info['version'], flush=True)
    (OUT / 'pypi-direct.json').write_text(json.dumps(rows, indent=2) + '\n')
    actions = {}
    for path in Path('.github/workflows').glob('*.yml'):
        for name, ref, version in re.findall(r'uses: ([\w./-]+)@([\w.\-]+)(?: # ([^\n]+))?', path.read_text()):
            repository = '/'.join(name.split('/')[:2])
            actions.setdefault(repository, {'previous_ref': ref, 'previous_version': version})
    extras = ['pre-commit/pre-commit-hooks', 'pre-commit/mirrors-clang-format',
              'google/googletest', 'google/benchmark', 'cpm-cmake/CPM.cmake',
              'microsoft/vcpkg', 'microsoft/vcpkg-tool', 'rhysd/actionlint',
              'doxygen/doxygen', 'python/cpython', 'Kitware/CMake', 'ninja-build/ninja',
              'dotnet/sdk', 'llvm/llvm-project']
    for repo in extras:
        actions.setdefault(repo, {})
    releases = {}
    for repo, previous in actions.items():
        response = subprocess.run(['gh', 'api', f'repos/{repo}/releases/latest'], capture_output=True, text=True)
        if response.returncode:
            tags = api(f'repos/{repo}/tags?per_page=5')
            release = {'tag_name': tags[0]['name'], 'body': 'No GitHub release; newest tag',
                       'html_url': f'https://github.com/{repo}/tags'}
        else:
            release = json.loads(response.stdout)
        tag = api(f"repos/{repo}/git/ref/tags/{release['tag_name']}")['object']
        while tag['type'] == 'tag':
            tag = api(f"repos/{repo}/git/tags/{tag['sha']}")['object']
        releases[repo] = {**previous, 'tag': release['tag_name'], 'sha': tag['sha'],
                          'published_at': release.get('published_at'), 'url': release['html_url'],
                          'body': release['body'], 'assets': [
                              {'name': a['name'], 'url': a['browser_download_url'], 'digest': a.get('digest')}
                              for a in release.get('assets', [])]}
        print(repo, previous.get('previous_version'), '->', release['tag_name'], tag['sha'], flush=True)
        (OUT / 'github-releases.json').write_text(json.dumps(releases, indent=2) + '\n')

if __name__ == '__main__':
    main()
