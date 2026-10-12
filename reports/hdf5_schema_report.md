# HDF5 schema report

Structure includes group/dataset attributes, dimensions, dtypes and storage features.

## Schema 0e3b2865443b56a8: 480 catalogs

Missing relative to union: []

| Path | Shape | dtype | Attributes |
|---|---|---|---|
| `/` | group | — | {} |
| `Computed` | group | — | {} |
| `Computed/Bound_DM_Rmax` | [1001] | float32 | {} |
| `Computed/Bound_DM_SigmaV` | [1001] | float32 | {} |
| `Computed/Bound_DM_Vmax` | [1001] | float32 | {} |
| `Computed/Bound_Star_Rmax` | [1001] | float32 | {} |
| `Computed/Bound_Star_SigmaV` | [1001] | float32 | {} |
| `Computed/Bound_Star_Vmax` | [1001] | float32 | {} |
| `Computed/Excl_Mdm_200c` | [1001] | float32 | {} |
| `Computed/Excl_Mstar_200c` | [1001] | float32 | {} |
| `Computed/Excl_Mtot_200c` | [1001] | float32 | {} |
| `Computed/Excl_R200c` | [1001] | float32 | {} |
| `Computed/Incl_Mdm_200c` | [1001] | float32 | {} |
| `Computed/Incl_Mstar_200c` | [1001] | float32 | {} |
| `Computed/Incl_Mtot_200c` | [1001] | float32 | {} |
| `Computed/Incl_R200c` | [1001] | float32 | {} |
| `Computed/Star_Mhalf_2D` | [1001] | float32 | {} |
| `Computed/Star_Mhalf_3D` | [1001] | float32 | {} |
| `Computed/Star_Rhalf_2D` | [1001] | float32 | {} |
| `Computed/Star_Rhalf_3D` | [1001] | float32 | {} |
| `Computed/Star_Sigma_2D` | [1001] | float32 | {} |
| `HBT` | group | — | {} |
| `HBT/BoundM200Crit` | [1001] | float32 | {} |
| `HBT/BoundR200CritComoving` | [1001] | float32 | {} |
| `HBT/ComovingAveragePosition` | [1001, 3] | float32 | {} |
| `HBT/ComovingMostBoundPosition` | [1001, 3] | float32 | {} |
| `HBT/Depth` | [1001] | int32 | {} |
| `HBT/HostHaloId` | [1001] | int32 | {} |
| `HBT/InertialTensor` | [1001, 6] | float32 | {} |
| `HBT/InertialTensorWeighted` | [1001, 6] | float32 | {} |
| `HBT/LastMaxMass` | [1001] | float32 | {} |
| `HBT/LastMaxVmaxPhysical` | [1001] | float32 | {} |
| `HBT/Mbound` | [1001] | float32 | {} |
| `HBT/MboundType` | [1001, 6] | float32 | {} |
| `HBT/MostBoundParticleId` | [1001] | int32 | {} |
| `HBT/Nbound` | [1001] | int32 | {} |
| `HBT/NboundType` | [1001, 6] | int32 | {} |
| `HBT/PhysicalAverageVelocity` | [1001, 3] | float32 | {} |
| `HBT/PhysicalMostBoundVelocity` | [1001, 3] | float32 | {} |
| `HBT/R2SigmaComoving` | [1001] | float32 | {} |
| `HBT/RHalfComoving` | [1001] | float32 | {} |
| `HBT/Rank` | [1001] | int32 | {} |
| `HBT/RmaxComoving` | [1001] | float32 | {} |
| `HBT/SinkTrackId` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfBirth` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfDeath` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfLastIsolation` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfLastMaxMass` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfLastMaxVmax` | [1001] | int32 | {} |
| `HBT/SnapshotIndexOfSink` | [1001] | int32 | {} |
| `HBT/SpecificAngularMomentum` | [1001, 3] | float32 | {} |
| `HBT/SpecificSelfKineticEnergy` | [1001] | float32 | {} |
| `HBT/SpecificSelfPotentialEnergy` | [1001] | float32 | {} |
| `HBT/TrackId` | [1001] | int32 | {} |
| `HBT/VmaxPhysical` | [1001] | float32 | {} |
| `Mock` | group | — | {} |
| `Mock/M_DM_Re_mean` | [1001] | float32 | {} |
| `Mock/M_dyn_mean` | [1001] | float32 | {} |
| `Mock/M_dyn_std` | [1001] | float32 | {} |
| `Mock/M_star_Re_mean` | [1001] | float32 | {} |
| `Mock/Re_mean` | [1001] | float32 | {} |
| `Mock/Re_std` | [1001] | float32 | {} |
| `Mock/f_DM_true_Re` | [1001] | float32 | {} |
| `Mock/f_bound` | [1001] | float32 | {} |
| `Mock/f_star_inferred` | [1001] | float32 | {} |
| `Mock/mbound` | [1001] | float32 | {} |
| `Mock/mstar_bound` | [1001] | float32 | {} |
| `Mock/mstar_over_mbound` | [1001] | float32 | {} |
| `Mock/n_proj` | [1001] | int32 | {} |
| `Mock/sigma_los_mean` | [1001] | float32 | {} |
| `Mock/sigma_los_std` | [1001] | float32 | {} |

Infinite values: 415900. NaN and integer -1 counts per field per simulation are in `dataset_statistics.csv`; -1 is not automatically an error. No monotonic mass constraint was imposed.

