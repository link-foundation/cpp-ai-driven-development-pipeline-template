import concurrent.futures, json, re, subprocess, urllib.parse, urllib.request
from pathlib import Path
out=Path('dev/log/issues/30/pulls/31/raw')
def get(item):
 name,version=item
 with urllib.request.urlopen('https://registry.npmjs.org/'+urllib.parse.quote(name,safe='')+'/latest') as r: meta=json.load(r)
 repo=meta.get('repository',{})
 repo=repo.get('url','') if isinstance(repo,dict) else repo
 match=re.search(r'github.com[:/]([^/]+/[^/#]+)',repo)
 result={'name':name,'version':version,'engines':meta.get('engines'),'repository':repo}
 if match:
  slug=match.group(1).removesuffix('.git'); major=version.split('.')[0]
  for tag in ('v'+major+'.0.0',major+'.0.0','v'+version):
   p=subprocess.run(['gh','api',f'repos/{slug}/releases/tags/{tag}'],capture_output=True,text=True)
   if p.returncode==0:
    release=json.loads(p.stdout); result.update(url=release['html_url'],notes=release.get('body')); break
 return result
items=json.loads(Path('package.json').read_text())['overrides'].items()
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: data=list(pool.map(get,items))
(out/'npm-major-migrations.json').write_text(json.dumps(data,indent=2)+'\n')
for d in data: print(d['name'],d['version'],d.get('url','NO RELEASE NOTES'), '\n',d.get('notes','')[:2500], '\n')
