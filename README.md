# TidalTrack Catalog

Time-dependent subhalo and stellar catalogs from 480 controlled N-body tidal-evolution simulations.

**Version: v0.1.0 — initial catalog distribution.** This version preserves the existing catalogs unchanged and documents known limitations. More complete scientific metadata and analysis tools will follow.

## Download and quick start

The catalog ZIP and its SHA256 checksum are distributed through the repository's [GitHub Releases](https://github.com/fhtouma/TidalTrack-Catalog/releases). The data are release assets, not part of the Git source checkout. Zenodo archival publication and DOI are pending; no DOI is claimed.

Download `tidaltrack-catalog-v0.1.0.zip` and `SHA256SUMS` from the v0.1.0 release, then run:

```bash
sha256sum -c SHA256SUMS
unzip tidaltrack-catalog-v0.1.0.zip -d data
python3 -m pip install -r requirements-audit.txt
python3 examples/read_catalog.py data/catalogs/Sim_0000/subhalo_properties.hdf5
```

The ZIP contains `catalogs/Sim_NNNN/subhalo_properties.hdf5`, `metadata/catalog_manifest.csv`, `metadata/simulations.csv`, this README, a structural schema report and the rights notice. Each catalog's size and SHA256 are listed in the manifest. The original HDF5 bytes are retained, including their NaNs and infinities.

## Scope

This release contains only the existing `subhalo_properties.hdf5` catalogs and supporting metadata, documentation and reading software. Particle snapshots, initial-condition particle data, HBT particle catalogs and intermediate products are excluded. Original simulation files remain unchanged.

The audit found all IDs `Sim_0000`–`Sim_0479`, matching the 480-row simulation registry. The catalogs total **200,373,120 bytes (191.091 MiB)**. They share one schema: 3 groups and 67 datasets, each with 1001 time rows. Floating-point datasets are float32 and integer datasets are int32. No HDF5 attributes, external links, external storage, or virtual datasets were found. Original numerical precision must be preserved; a future ZIP can preserve every source byte.

## Parameter coverage

Values below were checked against all per-simulation `params.json` files. Model descriptions follow the available generation code, whose historical correspondence to every run still needs confirmation.

| Parameter | Values |
|---|---|
| Input DM M200 | 1 code mass unit, nominally 10^10 solar masses |
| c2 | 5, 10 |
| s_001 | 0.6, 1.0, 1.2, 1.4, 1.8 |
| Input stellar mass / input DM M200 | 0.001, 0.01, 0.05 |
| Input stellar scale radius / R200 | 0.01, 0.02, 0.04, 0.1 |
| Sersic index | 0.5, 1, 2.5, 4 |
| Target particle number per input M200 | 1,000,000 |
| Host input M200; concentration | 100 code mass units; 10 |
| Initial apocentre | 100 kpc |
| Assigned pericentre | 5, 10, 20, 35, 50 kpc, coupled to c2 and s_001 |
| Redshift used in initial model | 0 |

The five varying model parameters form a 2 × 5 × 3 × 4 × 4 grid at one input mass. Orbits are assigned by the DM parameters, not independently sampled. The registry field `orbit_ecc` is **R_apo/R_peri**, not the usual eccentricity.

Available code builds an AGAMA Spheroid DM model (labelled Dekel–Zhao in its plots), with alpha=0.5, beta=3.5, an outer cutoff at 2 R200 and cutoffStrength=2; mass is anchored inside R200. Stars use a spherical Sersic model. Energy selection and a final 200 kpc pruning step affect the realized particle population. Do not treat nominal input parameters as measurements of the realized initial conditions.

## Catalog structure and definitions

| Group | Contents |
|---|---|
| `Computed` | Bound component sizes and kinematics; inclusive/exclusive spherical-overdensity measurements |
| `HBT` | Fields copied from HBT `Subhalos[0]` at each snapshot |
| `Mock` | Projected stellar measurements and a Wolf-style dynamical-mass estimator |

See [the full structural schema](reports/hdf5_schema_report.md) for dataset paths, dimensions and dtypes. That report is a structural inventory, not a completed physical dictionary of every HBT field.

Definitions verified in the current `extract_subhalo_properties.py`:

- `Mock/f_bound` = total HBT bound mass at row i divided by total HBT bound mass at row 0. This includes stars and is not a DM-only fraction. The identity was checked across all catalogs.
- `Computed/Star_Rhalf_2D` is a discrete projected half-mass radius in the xy plane. `Mock/Re_mean` averages interpolated projected half-mass radii over valid x, y and z sightlines. These are distinct estimators; neither directly measures luminosity.
- `Computed/Star_Sigma_2D` = `Star_Mhalf_2D / (pi * Star_Rhalf_2D**2)`, a surface mass density, not a velocity dispersion.
- `Computed/Bound_DM_Vmax` and its Rmax maximize sqrt(G M_DM(<r)/r) using bound DM alone; the analogous stellar fields use bound stars alone. Do not substitute the total-subhalo HBT Vmax without documenting the difference.
- `Computed/*_SigmaV` = sqrt((var(vx)+var(vy)+var(vz))/3), using the component's bound particles with population variances.
- `Mock/sigma_los_mean` averages mass-weighted LOS population dispersions inside each projected Re, with that aperture's own mean subtracted.
- The mock estimator is `M_dyn = 4 * sigma_los**2 * Re / G`. `M_star_Re_mean` and `M_DM_Re_mean` instead count true mass inside a **3D sphere of radius Re**. Their comparison is not an exactly matched-aperture mass comparison.
- Computed positions and velocities are relative to HBT's most-bound-particle centre and velocity. Inclusive mass measurements use all satellite particles in the snapshot, including debris; they do not add analytic host mass.

Input and runtime configurations identify nominal units of kpc, 10^10 solar masses and km/s. Surface mass density is consequently in 10^10 solar masses/kpc². The code time unit is length/velocity, approximately 0.978 Gyr. All runtime configurations specify non-cosmological integration, first output 0 and interval 0.02 through 20 code time units. Catalog rows are snapshot indices; **no explicit time dataset exists**. Headers at snapshots 0, 500 and 1000 were independently checked for three simulations and contain times 0, 10 and 20. This is a sample check, not verification of every snapshot time.

DM (PartType1, softening class 0) and stars (PartType4, class 3) use the same configured softening: 0.026666 or 0.013333 kpc. These are configuration values; the force-kernel convention still needs a verified code/build reference.

## Data quality: read before use

**Initial release with known limitations.** File readability passed for all 480 catalogs, but this is not a scientific-validation pass.

- `HBT/BoundR200CritComoving` contains **415,900 infinite values across all 480 catalogs**. Raw HBT snapshot-zero records in three simulations also contain infinity, so those sampled cases predate catalog extraction. The cause and treatment require review. Do not use this field as a valid physical radius.
- NaNs occur in derived fields. The extractor uses 50-particle thresholds for component half-mass radii and kinematics, and separate mock thresholds (20 bound stars, 10 bound DM particles and 10 stars per projected aperture). It also uses NaN/-1 for unprocessed entries. No explicit processing-success or termination flag is stored.
- All 480 `HBT/Mbound` arrays have 1001 finite entries, no internal gaps, and HBT TrackId=0 throughout. This does not establish that every derived measurement is valid.
- Particle counts in `params.json` disagree with IC headers for **478 simulations**. The generator records counts before final pruning. IC header counts should be used for realized resolution, subject to checking their consistency with the executed run.
- The extractor casts HBT integers to int32 and other numbers to float32. These are properties of the existing catalogs; packaging will not restore lost upstream precision or downcast further.
- Available generator variants and regeneration scripts do not establish the precise source version used for every run. Random seeds, build versions and convergence criteria are not established by this audit.
- Bound-mass fluctuations are allowed; no artificial monotonicity requirement is imposed.

See [scientific questions and evidence](reports/missing_metadata.md) and [per-field numerical statistics](reports/dataset_statistics.csv).

## Reproduce the audit

Requirements: Python 3, NumPy and h5py. The audit ran successfully with the existing system Python and h5py 3.10.0. Optional isolated installation:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-audit.txt
```

From this working directory, replace `/path/to/tt` with the private source root:

```bash
python3 scripts/audit_catalogs.py --root /path/to/tt
python3 scripts/check_source_samples.py --root /path/to/tt
```

The script reads the immediate `Sim_NNNN` directories, catalogs, small configuration files and IC headers. It does not load particle arrays or execute simulation/analysis source scripts. It writes only to this separate working directory. Full numerical scans are limited to catalog arrays, read in blocks. Compression trials run in memory and verify exact byte recovery. An alternate output directory can be supplied with `--out`.

Outputs:

- [Catalog inventory](reports/catalog_inventory.md), with portable paths and SHA256 in `reports/inventory.csv`.
- [HDF5 schema](reports/hdf5_schema_report.md), with numerical counts in `reports/dataset_statistics.csv`.
- [Data volume and compression](reports/data_volume_report.md).
- [Phase-1 validation status](reports/validation_report.md).
- [Outstanding metadata and scientific questions](reports/missing_metadata.md).
- `private/`: local source paths, configuration exports and detailed schema evidence. This directory is excluded from Git and must not be uploaded.

## Packaging and verification

```bash
python3 scripts/package_catalogs.py --root /path/to/tt
python3 scripts/package_catalogs.py --verify dist/tidaltrack-catalog-v0.1.0.zip
```

Packaging reads only the 480 catalog files and small per-run parameter JSON files. It checks source hashes against the audit inventory, uses fixed ZIP timestamps and sorted simulation IDs, then verifies all archived catalog hashes and membership. Reproducibility assumes identical source data, documentation and Python/zlib versions.

`metadata/simulations.csv` retains the input JSON parameter names. `N_dm_actual` and `N_star_actual` are the original JSON values, often recorded before pruning; use the separately labelled `ic_header_N_dm` and `ic_header_N_star` for the realized IC counts. Nominal parameters are not measurements of the realized system. `catalog_path` is relative to the extracted ZIP root.

## Citation, rights and future versions

Authors: **Feihong He and Fangzhou Jiang**. Data, metadata and scientific documentation: **CC BY 4.0** ([LICENSE-DATA](LICENSE-DATA)). New scripts: **MIT** ([LICENSE-CODE](LICENSE-CODE)). See [NOTICE.md](NOTICE.md) for scope.

Suggested citation: He, Feihong, and Jiang, Fangzhou. *TidalTrack Catalog*, version 0.1.0. https://github.com/fhtouma/TidalTrack-Catalog. See [CITATION.cff](CITATION.cff). A Zenodo DOI and paper reference will be added when available; affiliations and ORCIDs have not been supplied.

Later releases will improve the physical field dictionary, provenance and quality flags, add analysis examples and provide a Zenodo archive. Corrections to numerical data will be explicitly versioned; this initial version preserves the current files.
