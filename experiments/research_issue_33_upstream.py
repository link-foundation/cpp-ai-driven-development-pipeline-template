#!/usr/bin/env python3
"""Refresh upstream workaround reports and retain their full discussion context."""
import json
import re
import subprocess
from pathlib import Path

OUT = Path('dev/log/issues/33/pulls/34/research/upstream')
OUT.mkdir(exist_ok=True)
text = Path('dev/log/issues/30/pulls/31/UPSTREAM.md').read_text()
refs = sorted(set(re.findall(r'https://github.com/([^/]+/[^/]+)/(issues|pull)/(\d+)', text)))
summary = []
for repo, kind, number in refs:
    command = ['gh', 'issue' if kind == 'issues' else 'pr', 'view', number,
               '--repo', repo, '--json', 'title,body,comments,state,url']
    result = subprocess.run(command, capture_output=True, text=True)
    filename = repo.replace('/', '-') + '-' + number + '.json'
    if result.returncode:
        print('ERROR', repo, number, result.stderr, flush=True)
        continue
    payload = json.loads(result.stdout)
    (OUT / filename).write_text(json.dumps(payload, indent=2) + '\n')
    summary.append({'repository': repo, 'number': number,
                    'title': payload['title'], 'state': payload['state'], 'url': payload['url']})
    print(repo, number, payload['state'], payload['title'], flush=True)
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
