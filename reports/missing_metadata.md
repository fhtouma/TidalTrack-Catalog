# Scientific review gate — Phase 1

The initial audit identified the questions below. The owner subsequently authorized an initial public distribution of the current catalogs, with scientific refinements deferred. These questions document limitations; they are not a publication approval gate.

## Scientific follow-up

1. **Invalid upstream radius:** `HBT/BoundR200CritComoving` has 415,900 infinite entries (86.56% of its 480,480 entries), distributed across all simulations. All other catalog fields have zero infinities. Raw `SubSnap_000.hdf5` records were checked for Sim_0000, Sim_0001 and Sim_0479: their float32 radius is already infinite, while BoundM200Crit is finite. Decide whether to preserve the original catalog with a prominently documented unusable field, or commission a separately versioned corrected product. Do not silently replace it with `Computed/Excl_R200c`: the definitions differ. The related `HBT/BoundM200Crit` also needs scrutiny.
2. **Historical provenance:** confirm which IC generator, stellar energy-selection recipe, regeneration subset and Gadget/HBT builds produced these runs. `IC_generate.py`, `IC_generate_bak.py` and `regenerate_n05_sims.py` coexist; the latter targets Re_Rvir=0.04, n_sersic=0.5. Current source inspection alone cannot establish historical use. Random seeds and exact binary/source identities for the runs are unverified.
3. **Validity and termination:** supply the scientific usability/convergence criteria and intended treatment of low-particle outputs. No explicit catalog flag distinguishes physical disruption, failed extraction and unmet thresholds. A completed registry status and finite HBT mass are not sufficient quality flags.

## Recovered facts and interpretation limits

- All 480 catalog files share one structure, have no attributes and contain 67 datasets in Computed/HBT/Mock. Files are readable; no non-hard HDF5 links, virtual datasets or external dataset storage were detected.
- Every HBT/Mbound row is finite, with indices 0–1000 and no internal gaps. TrackId is 0 throughout. Mock/f_bound agrees with total Mbound/Mbound[0] across the entire catalog set.
- All runtime used-values files specify the same base units and non-cosmological output timing. Nine header checks (three simulations × snapshots 0/500/1000) match the configured schedule. The full 480,480-header time audit has not been run. UnitLength is rounded in the used-values text relative to the input parameter file; avoid claiming unwarranted conversion precision.
- IC NumPart_Total disagrees with the JSON count pair for 478/480 runs. See `ic_header_check.csv`. The available code writes N_dm_actual/N_star_actual before pruning in `create_gadget_ic`; those JSON keys must not be published as verified final particle numbers.
- The parameter grid is fully represented. The registry field named orbit_ecc is an apocentre/pericentre ratio, not conventional eccentricity. Orbits covary with c2 and s_001.
- The source anchors the DM profile inside R200 and assigns input stellar mass f_star × input DM M200; f_star is not a measured stellar fraction of the final bound total.
- The source supplies a Sersic scale radius to AGAMA. Exact library-version semantics and agreement with the realized, energy-selected initial population remain to be established before describing this as a measured initial effective radius.
- Softening type/class mappings and values are recoverable. Kernel convention, code build and numerical convergence criteria remain unverified.
- Current extraction code uses h=0.7 to set the critical density, whereas the non-cosmological snapshot header HubbleParam is 1. These serve different code roles and should be documented explicitly, not used interchangeably.
- Local HBT source `src/subhalo.cpp` routes BoundR200CritComoving to `Cosmology_t::SphericalOverdensitySize` in `src/snapshot.cpp`, whose radius calculation divides by a density involving Hz² and ScaleFactor³. A zero density could yield infinity; this is a hypothesis, not an established diagnosis of the executed binary.
- HBT field meanings beyond the verified mass, ID and copying behavior need a field-by-field source/build review. Tensor ordering, energy normalization, sentinels, physical/comoving labels and event indices must not be guessed.
- Existing catalogs already downcast HBT output to float32/int32. This release must preserve these bytes and document upstream precision limits.

## Evidence

`source_checksums.csv` records hashes of available root-level Python sources and the registry. Definitions were inspected in `extract_subhalo_properties.py` (thresholds, geometry, frames, normalization and serialization), `IC_generate.py` (profile construction, units, orbit, energy cuts, counts and pruning), `step1_make_registry.py` (parameter grid and orbit mapping), `step2_build_sims.py` (softening assignment) and `run_hbt_batch.py` (HBT executable selection). Per-run parameter/configuration exports and absolute source manifest are private. Available source files were never executed.

## Remaining publication metadata

The owner confirmed authors Feihong He and Fangzhou Jiang (in that order), CC BY 4.0 for data and MIT for new code. Affiliations and a paper reference remain unspecified. The owner has authorized publication of the current catalog version on GitHub/Zenodo. Account authentication and the metadata required by Zenodo must still be supplied.
