#!/usr/bin/env python3
"""Read-only, bounded Phase-1 audit. Never reads particle arrays or uploads data."""
import argparse, collections, csv, hashlib, io, json, pathlib, zipfile
import h5py
import numpy as np

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def config(path):
    result = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.split('%')[0].split('#')[0].split(';')[0].strip()
            parts = line.split()
            if len(parts) >= 2: result[parts[0]] = parts[1]
    return result

def jsonable(x):
    if isinstance(x, bytes): return x.decode('utf-8', errors='backslashreplace')
    if isinstance(x, np.ndarray): return jsonable(x.tolist())
    if isinstance(x, np.generic): return jsonable(x.item())
    if isinstance(x, list): return [jsonable(v) for v in x]
    return x

def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    a = ap.parse_args(); root = a.root.resolve(); out = a.out.resolve()
    if out == root or root in out.parents: raise SystemExit('Output must be outside source tree')
    reports = out/'reports'; private = out/'private'
    reports.mkdir(parents=True, exist_ok=True); private.mkdir(exist_ok=True)
    dirs = sorted(p for p in root.glob('Sim_[0-9][0-9][0-9][0-9]') if p.is_dir())
    files = [p/'subhalo_properties.hdf5' for p in dirs if (p/'subhalo_properties.hdf5').is_file()]
    ic_rows=[]
    records=[]; schemas={}; variants=collections.defaultdict(list); stats=[]; issues=[]; configs=[]; params=[]
    for path in files:
        sid=path.parent.name; before=path.stat(); row={'simulation_id':sid,'relative_path':f'{sid}/{path.name}','bytes':before.st_size,'sha256':sha(path)}
        schema={}; links=[]; seen=set()
        try:
            with h5py.File(path,'r') as f:
                def walk(g, prefix=''):
                    addr=h5py.h5o.get_info(g.id).addr
                    if addr in seen: return
                    seen.add(addr)
                    schema[prefix or '/']={'kind':'group','attrs':{k:jsonable(v) for k,v in g.attrs.items()}}
                    for key in g:
                        name=f'{prefix}/{key}'.lstrip('/'); link=g.get(key,getlink=True)
                        if not isinstance(link,h5py.HardLink):
                            links.append({'path':name,'type':type(link).__name__}); continue
                        obj=g[key]
                        if isinstance(obj,h5py.Group): walk(obj,name); continue
                        schema[name]={'kind':'dataset','shape':list(obj.shape),'dtype':str(obj.dtype),'attrs':{k:jsonable(v) for k,v in obj.attrs.items()},'compression':obj.compression,'chunks':obj.chunks,'virtual':obj.is_virtual,'external':obj.external}
                        if obj.is_virtual or obj.external:
                            issues.append(f'{sid}: external/virtual dataset {name}; payload not read'); continue
                        # Catalog datasets are small; bounded slices also support larger catalogs.
                        nan=inf=neg=0; minimum=maximum=None
                        blocks=(obj[i:i+4096] for i in range(0,obj.shape[0],4096)) if obj.ndim else [obj[()]]
                        for v in blocks:
                            if np.issubdtype(obj.dtype,np.number):
                                nan+=int(np.isnan(v).sum()); inf+=int(np.isinf(v).sum()); neg+=int((v==-1).sum())
                                good=np.asarray(v)[np.isfinite(v)]
                                if good.size:
                                    lo=float(good.min()); hi=float(good.max())
                                    minimum=lo if minimum is None else min(minimum,lo); maximum=hi if maximum is None else max(maximum,hi)
                        stats.append({'simulation_id':sid,'dataset':name,'nan':nan,'inf':inf,'minus_one':neg,'min':minimum,'max':maximum})
                walk(f)
                if 'HBT/Mbound' in f:
                    v=f['HBT/Mbound'][:]; idx=np.flatnonzero(np.isfinite(v))
                    row.update(finite_mass_rows=len(idx),first_mass_index=int(idx[0]) if len(idx) else '',last_mass_index=int(idx[-1]) if len(idx) else '',mass_internal_gaps=int(idx[-1]-idx[0]+1-len(idx)) if len(idx) else '')
                if 'HBT/TrackId' in f:
                    v=f['HBT/TrackId'][:]; row['nonnegative_track_ids']=','.join(map(str,np.unique(v[v>=0])))
                if 'Mock/f_bound' in f and 'HBT/Mbound' in f:
                    m=f['HBT/Mbound'][:]; v=f['Mock/f_bound'][:]; mask=np.isfinite(v)&np.isfinite(m)
                    row['f_bound_matches_total_mass']=bool(np.allclose(v[mask],m[mask]/m[0],rtol=2e-6)) if mask.any() and m[0]>0 else 'uncheckable'
            row['status']='PASS' if not links else 'WARNING'
        except Exception as e:
            row['status']='FAIL'; issues.append(f'{sid}: {type(e).__name__}: {e}')
        if links: issues.append(f'{sid}: links {links}')
        after=path.stat(); row['stable_during_read']=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        signature=hashlib.sha256(json.dumps(schema,sort_keys=True).encode()).hexdigest()[:16]
        row['schema_id']=signature; variants[signature].append(sid); schemas[signature]=schema; records.append(row)
        p=path.parent/'params.json'
        params.append({'simulation_id':sid,**(json.loads(p.read_text()) if p.exists() else {'missing':True})})
        with h5py.File(path.parent/'ics.hdf5','r') as ic:
            counts=ic['Header'].attrs['NumPart_Total']; par=params[-1]
            ic_rows.append({'simulation_id':sid,'ic_dm_count':int(counts[1]),'ic_star_count':int(counts[4]),'params_dm_count':par.get('N_dm_actual'),'params_star_count':par.get('N_star_actual'),'matches':int(counts[1])==par.get('N_dm_actual') and int(counts[4])==par.get('N_star_actual')})
        cfg=config(path.parent/'param.txt-usedvalues') or config(path.parent/'param.txt')
        configs.append({'simulation_id':sid,**cfg})
        if len(records)%80==0: print(f'Audited {len(records)}/{len(files)}',flush=True)
    write_csv(reports/'ic_header_check.csv',ic_rows)
    write_csv(reports/'inventory.csv',records); write_csv(reports/'dataset_statistics.csv',stats)
    write_csv(private/'source_manifest.csv',[{**r,'source_path':str(root/r['relative_path'])} for r in records])
    write_csv(private/'parameters.csv',params); write_csv(private/'runtime_configurations.csv',configs)
    (private/'schemas.json').write_text(json.dumps(schemas,indent=2))
    sources=[{'file':p.name,'sha256':sha(p)} for p in sorted(root.glob('*.py'))]+[{'file':'sim_registry.csv','sha256':sha(root/'sim_registry.csv')}]
    write_csv(reports/'source_checksums.csv',sources)
    total=sum(r['bytes'] for r in records)
    sizes=sorted(files,key=lambda p:p.stat().st_size)
    samples=list(dict.fromkeys(sizes[i] for i in [0,len(sizes)//4,len(sizes)//2,3*len(sizes)//4,len(sizes)-1])) if sizes else []
    compression=[]
    for p in samples:
        raw=p.read_bytes(); buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z: z.writestr(f'{p.parent.name}/{p.name}',raw)
        with zipfile.ZipFile(buf) as z: assert z.read(z.namelist()[0])==raw
        compression.append({'simulation_id':p.parent.name,'original_bytes':len(raw),'zip_bytes':len(buf.getvalue()),'ratio':len(buf.getvalue())/len(raw)})
    write_csv(reports/'compression_sample.csv',compression)
    registry=list(csv.DictReader((root/'sim_registry.csv').open())); expected={r['ID'] for r in registry}; actual={r['simulation_id'] for r in records}
    summary={'catalog_count':len(files),'total_bytes':total,'schema_variants':{k:len(v) for k,v in variants.items()},'status_counts':dict(collections.Counter(r['status'] for r in records)),'missing_registry_ids':sorted(expected-actual),'unexpected_ids':sorted(actual-expected),'issues':issues,'ic_count_mismatches':sum(not r['matches'] for r in ic_rows),'infinite_values':sum(s['inf'] for s in stats),'unstable_files':[r['simulation_id'] for r in records if not r['stable_during_read']]}
    (reports/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    def md(name,body): (reports/name).write_text(body+'\n')
    md('catalog_inventory.md',f'# Catalog inventory\n\nRead-only audit of immediate `Sim_NNNN/subhalo_properties.hdf5` files. No particle arrays were read.\n\n- Catalogs: {len(files)}; simulation directories: {len(dirs)}; registry rows: {len(registry)}.\n- Total bytes: {total:,} ({total/1024**2:.3f} MiB).\n- File readability status (not scientific validity): {summary["status_counts"]}.\n- Missing registry IDs: {summary["missing_registry_ids"]}. Unexpected IDs: {summary["unexpected_ids"]}.\n- Files changed during inspection: {summary["unstable_files"]}.\n\nSee `inventory.csv` for IDs, relative paths, SHA256 and coverage. Finite mass coverage is not a success/termination flag. `private/source_manifest.csv` contains local absolute paths and must never be published.\n\nIssues: '+ ('; '.join(issues) or 'None detected in catalog reading.'))
    body='# HDF5 schema report\n\nStructure includes group/dataset attributes, dimensions, dtypes and storage features.\n'
    all_fields=set().union(*(set(s) for s in schemas.values())) if schemas else set()
    for sig,schema in schemas.items():
        body+=f'\n## Schema {sig}: {len(variants[sig])} catalogs\n\nMissing relative to union: {sorted(all_fields-set(schema))}\n\n| Path | Shape | dtype | Attributes |\n|---|---|---|---|\n'
        for name,item in schema.items(): body+=f'| `{name}` | {item.get("shape","group")} | {item.get("dtype", "—")} | {json.dumps(item["attrs"])} |\n'
    body+=f'\nInfinite values: {summary["infinite_values"]}. NaN and integer -1 counts per field per simulation are in `dataset_statistics.csv`; -1 is not automatically an error. No monotonic mass constraint was imposed.\n'
    md('hdf5_schema_report.md',body)
    ratio=sum(r['zip_bytes'] for r in compression)/sum(r['original_bytes'] for r in compression) if compression else 1
    md('data_volume_report.md',f'# Data volume\n\nOriginal catalogs: {total:,} bytes ({total/1024**2:.3f} MiB).\n\nZIP DEFLATE level 6 tested on {len(samples)} catalogs selected at size quantiles, with byte-for-byte decompression verification. Combined archive/original ratio: {ratio:.4f}. Extrapolated full archive size: {total*ratio/1024**2:.2f} MiB; this is an estimate, not a built archive. See `compression_sample.csv`.\n\nA single catalog-only ZIP appears practical at this size. Preserve original HDF5 bytes, names under simulation IDs, and manifest checksums. Do not add snapshots, ICs, particle arrays or subcat files. Final packaging awaits Phase-1 scientific review. No archive or public release has been created.')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
