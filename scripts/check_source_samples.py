#!/usr/bin/env python3
"""Reproduce the limited raw-HBT and snapshot-header cross-checks (no particles)."""
import argparse, json
from pathlib import Path
import h5py
import numpy as np
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root', type=Path, required=True)
ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'reports/source_samples.json')
a=ap.parse_args()
if a.out.resolve()==a.root.resolve() or a.root.resolve() in a.out.resolve().parents:
    raise SystemExit('Output must be outside source tree')
rows=[]
for sid in ['Sim_0000','Sim_0001','Sim_0479']:
    for i in [0,500,1000]:
        with h5py.File(a.root/sid/'snapshots'/f'snap_{i:03d}.hdf5','r') as f:
            rows.append({'simulation_id':sid,'snapshot':i,'header_time':float(f['Header'].attrs['Time'])})
    with h5py.File(a.root/sid/'subcat'/'SubSnap_000.hdf5','r') as f:
        d=f['Subhalos']; r=d[0]
        rows.append({'simulation_id':sid,'raw_hbt_snapshot':0,'radius_dtype':str(d.dtype['BoundR200CritComoving']),'radius_is_infinite':bool(np.isinf(r['BoundR200CritComoving'])),'BoundM200Crit':float(r['BoundM200Crit'])})
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(rows,indent=2)+'\n')
print(f'Wrote {len(rows)} sample checks to {a.out.name}')
