# Phase-1 validation status

This is a source audit, not final release acceptance. Scientific status: **initial distribution with documented warnings**. The owner authorized publication without waiting for full scientific refinement.

| Check | State | Evidence |
|---|---|---|
| Registry membership and unique source IDs | PASS | 480/480; no missing or extra IDs |
| Full catalog payload readability | PASS | 480 catalogs inspected; no read exceptions |
| Structure consistency | PASS | One schema; 67 datasets, three groups |
| Source stability during inspection | PASS | No size/mtime changes |
| Link and external storage inspection | PASS | No non-hard links, external storage or VDS |
| Catalog source SHA256 | PASS | Hash recorded for every original file; no release copy exists yet |
| HBT mass coverage | PASS | 1001 finite entries per simulation, indices 0–1000 |
| Track identity | PASS | HBT TrackId=0 throughout |
| Mock bound fraction formula | PASS | Agrees with total Mbound/Mbound[0] in all catalogs |
| Inf values | WARNING | 415,900 in HBT/BoundR200CritComoving; unsuitable for scientific use pending review |
| NaN/sentinel interpretation | WARNING | Per-field statistics recorded; catalog lacks explicit reason flags |
| Realized particle resolution | WARNING | 478 JSON/header count-pair mismatches; header counts recorded |
| Time axis | WARNING | Configuration recovered; nine sampled headers agree, full header audit pending |
| Lossless compression | PASS | Five size-quantile samples recovered byte-for-byte |
| Source versions and scientific convergence | PENDING | Historical build/generator mapping and criteria unverified |
| Final packaging and DOI | SEE RELEASE REPORT | See package_verification.json for archive checks; Zenodo DOI pending |

The final audit script was executed over all 480 source catalogs. Both Python scripts passed bytecode compilation. No simulation or extraction script was executed, and no source data was modified.
