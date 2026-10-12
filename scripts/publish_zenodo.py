#!/usr/bin/env python3
"""Upload and publish the prepared release on Zenodo; requires explicit --publish."""
import argparse,hashlib,json,os
from pathlib import Path
from urllib.parse import quote,urlparse
import requests
from package_catalogs import verify
BASE=Path(__file__).resolve().parents[1]
API='https://zenodo.org/api/deposit/depositions'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--token-file',type=Path,default=BASE/'private/zenodo-token')
    ap.add_argument('--publish',action='store_true')
    a=ap.parse_args()
    archive=BASE/'dist/tidaltrack-catalog-v0.1.0.zip'; report=verify(archive)
    if not a.publish:
        print(json.dumps({'archive':report,'mode':'local validation only; use --publish to upload and publish'},indent=2)); return
    token=os.environ.get('ZENODO_ACCESS_TOKEN') or (a.token_file.read_text().strip() if a.token_file.exists() else '')
    if not token: raise SystemExit('Zenodo token missing; supply --token-file or ZENODO_ACCESS_TOKEN')
    state_path=BASE/'private/zenodo-state.json'
    sess=requests.Session(); sess.headers['Authorization']='Bearer '+token
    def call(method,url,**kwargs):
        if urlparse(url).scheme!='https' or urlparse(url).hostname!='zenodo.org': raise ValueError('Unexpected API host')
        r=sess.request(method,url,timeout=(20,300),allow_redirects=False,**kwargs)
        if not 200<=r.status_code<300:
            raise SystemExit(f'Zenodo {method} failed with HTTP {r.status_code}: '+r.text[:1000].replace(token,'[REDACTED]'))
        return r.json() if r.content else {}
    metadata=json.loads((BASE/'release/zenodo-metadata.json').read_text())
    if state_path.exists():
        state=json.loads(state_path.read_text())
        if state['archive_sha256']!=report['archive_sha256']: raise SystemExit('Existing deposition belongs to different archive; inspect private state before continuing')
        dep=call('GET',f'{API}/{state["id"]}')
    else:
        dep=call('POST',API,json=metadata)
        state={'id':dep['id'],'archive_sha256':report['archive_sha256']}
        state_path.write_text(json.dumps(state,indent=2)+'\n'); state_path.chmod(0o600)
    if dep.get('submitted'):
        print(json.dumps({'already_published':True,'id':dep['id'],'doi':dep.get('doi'),'url':dep.get('links',{}).get('html')},indent=2)); return
    call('PUT',f'{API}/{dep["id"]}',json=metadata)
    files=[archive,BASE/'dist/SHA256SUMS',BASE/'README.md',BASE/'metadata/catalog_manifest.csv',BASE/'metadata/simulations.csv',BASE/'CITATION.cff',BASE/'LICENSE-DATA',BASE/'LICENSE-CODE']
    existing={x['filename']:x for x in call('GET',f'{API}/{dep["id"]}/files')}
    if set(existing)-{p.name for p in files}: raise SystemExit('Unexpected files in deposition; inspect before publication')
    for path in files:
        checksum=hashlib.md5(path.read_bytes()).hexdigest()
        if path.name in existing:
            remote=existing[path.name]['checksum'].removeprefix('md5:')
            if remote!=checksum: raise SystemExit(f'Existing remote file differs: {path.name}')
            continue
        print('Uploading',path.name,flush=True)
        with path.open('rb') as f:
            data=call('PUT',dep['links']['bucket']+'/'+quote(path.name),data=f,headers={'Content-Type':'application/octet-stream'})
        if data.get('checksum','').removeprefix('md5:')!=checksum: raise SystemExit('Uploaded file checksum mismatch')
    remote=call('GET',f'{API}/{dep["id"]}/files')
    if {x['filename'] for x in remote}!={p.name for p in files}: raise SystemExit('Remote membership mismatch')
    for path in files:
        item=next(x for x in remote if x['filename']==path.name)
        if item['checksum'].removeprefix('md5:')!=hashlib.md5(path.read_bytes()).hexdigest(): raise SystemExit('Remote checksum mismatch')
    call('POST',f'{API}/{dep["id"]}/actions/publish')
    published=call('GET',f'{API}/{dep["id"]}')
    if not published.get('submitted'): raise SystemExit('Publication not yet confirmed; inspect deposition state')
    result={'id':published['id'],'doi':published.get('doi'),'url':published.get('links',{}).get('html'),'archive_sha256':report['archive_sha256']}
    (BASE/'private/zenodo-publication.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
