# Data volume

Original catalogs: 200,373,120 bytes (191.091 MiB).

ZIP DEFLATE level 6 tested on 5 catalogs selected at size quantiles, with byte-for-byte decompression verification. Combined archive/original ratio: 0.4286. Extrapolated full archive size: 81.89 MiB; this is an estimate, not a built archive. See `compression_sample.csv`.

A single catalog-only ZIP appears practical at this size. Preserve original HDF5 bytes, names under simulation IDs, and manifest checksums. Do not add snapshots, ICs, particle arrays or subcat files. See `package_verification.json` for the subsequently built archive size and full-file verification.
