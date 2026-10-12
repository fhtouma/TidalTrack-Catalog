#!/usr/bin/env python3
"""Build and verify a catalog-only ZIP without changing original HDF5 bytes."""
import argparse,csv,hashlib,io,json,os
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
BASE=Path(__file__).resolve().parents[1]
VERSION='v0.1.0'
def digest(data): return hashlib.sha256(data).hexdigest()
def csv_bytes(rows):
    out=io.StringIO(newline=''); w=csv.DictWriter(out,list(rows[0])); w.writeheader(); w.writerows(rows)
    return out.getvalue().encode()
def verify(path):
    with ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)): raise ValueError('Duplicate archive members')
        for name in names:
            if name.startswith('/') or '..' in Path(name).parts: raise ValueError('Unsafe archive path')
        rows=list(csv.DictReader(io.StringIO(z.read('metadata/catalog_manifest.csv').decode())))
        if len(rows)!=480 or len({r['simulation_id'] for r in rows})!=480: raise ValueError('Expected 480 unique catalogs')
        expected={r['catalog_path'] for r in rows}
        if {n for n in names if n.endswith('.hdf5')}!=expected: raise ValueError('Catalog membership mismatch')
        for row in rows:
            data=z.read(row['catalog_path'])
            if digest(data)!=row['sha256'] or len(data)!=int(row['bytes']): raise ValueError(f'Checksum/size mismatch: {row["simulation_id"]}')
        allowed=expected|{'metadata/catalog_manifest.csv','metadata/simulations.csv','README.md','reports/hdf5_schema_report.md','NOTICE.md','LICENSE-DATA','LICENSE-CODE','CITATION.cff'}
        if set(names)!=allowed: raise ValueError('Unexpected/missing archive members')
    return {'catalog_count':len(rows),'catalog_bytes':sum(int(r['bytes']) for r in rows),'archive_bytes':path.stat().st_size,'archive_sha256':digest(path.read_bytes()),'sha256_verification':'PASS','membership_verification':'PASS'}
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path); ap.add_argument('--verify',type=Path); a=ap.parse_args()
    if a.verify:
        print(json.dumps(verify(a.verify),indent=2)); return
    if a.root is None: ap.error('--root is required when building')
    root=a.root.resolve()
    if root==BASE or root in BASE.parents: raise ValueError('Working directory must be outside source root')
    inv=list(csv.DictReader((BASE/'reports/inventory.csv').open()))
    if len(inv)!=480: raise ValueError('Expected 480 audited catalogs')
    ic={r['simulation_id']:r for r in csv.DictReader((BASE/'reports/ic_header_check.csv').open())}
    manifest=[]; metadata=[]
    for row in inv:
        sid=row['simulation_id']; p=root/sid/'subhalo_properties.hdf5'
        if digest(p.read_bytes())!=row['sha256']: raise ValueError(f'Source changed since audit: {sid}')
        manifest.append({'simulation_id':sid,'catalog_path':f'catalogs/{sid}/subhalo_properties.hdf5','bytes':row['bytes'],'sha256':row['sha256'],'archive':f'tidaltrack-catalog-{VERSION}.zip'})
        par=json.loads((root/sid/'params.json').read_text())
        metadata.append({'simulation_id':sid,**par,'ic_header_N_dm':ic[sid]['ic_dm_count'],'ic_header_N_star':ic[sid]['ic_star_count'],'catalog_path':manifest[-1]['catalog_path']})
    (BASE/'metadata/catalog_manifest.csv').write_bytes(csv_bytes(manifest))
    (BASE/'metadata/simulations.csv').write_bytes(csv_bytes(metadata))
    out=BASE/'dist'/f'tidaltrack-catalog-{VERSION}.zip'; tmp=out.with_suffix('.zip.partial')
    def add(z,name,data):
        info=ZipInfo(name,date_time=(2026,10,12,0,0,0)); info.compress_type=ZIP_DEFLATED; info.create_system=3; info.external_attr=0o100644<<16
        z.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=6)
    with ZipFile(tmp,'w') as z:
        for name in ['README.md','NOTICE.md','LICENSE-DATA','LICENSE-CODE','CITATION.cff','metadata/catalog_manifest.csv','metadata/simulations.csv','reports/hdf5_schema_report.md']: add(z,name,(BASE/name).read_bytes())
        for row in manifest:
            data=(root/row['simulation_id']/'subhalo_properties.hdf5').read_bytes()
            if digest(data)!=row['sha256']: raise ValueError('Source changed during packaging')
            add(z,row['catalog_path'],data)
    result=verify(tmp); os.replace(tmp,out)
    (BASE/'dist/SHA256SUMS').write_text(f'{result["archive_sha256"]}  {out.name}\n')
    (BASE/'reports/package_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
