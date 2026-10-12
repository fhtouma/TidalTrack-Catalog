#!/usr/bin/env python3
"""Inspect one catalog: python examples/read_catalog.py /path/to/catalog.hdf5"""
import argparse
import h5py
import numpy as np
ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('catalog'); a=ap.parse_args()
with h5py.File(a.catalog,'r') as f:
    print('Groups:',', '.join(f.keys()))
    m=f['HBT/Mbound'][:]
    frac=f['Mock/f_bound'][:]
    print('Time rows:',len(m),'finite total bound masses:',np.isfinite(m).sum())
    print('Initial/final total bound mass [1e10 Msun]:',m[0],m[-1])
    print('Initial/final total bound fraction:',frac[0],frac[-1])
    print('Invalid HBT BoundR200CritComoving values:',np.count_nonzero(~np.isfinite(f['HBT/BoundR200CritComoving'][:])))
