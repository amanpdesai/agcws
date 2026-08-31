# Liberty inputs

These copied inputs support reproducible local/container runs. Do not modify
them in place.

| File | Role | Original path | SHA-256 |
|---|---|---|---|
| `sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib` | Primary Sky130 HD TT | `/opt/eda/ChipSTA/test/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib` | `92eb4e93a3d4c2563018ac81cdec2f02fdeaced9b39337ed5c141fa63e0ad8f8` |
| `nangate45/Nangate45_typ.lib` | Secondary cross-PDK check | `/opt/eda/ChipSTA/test/nangate45/Nangate45_typ.lib` | `2efd0b32eb580e4e60e72fc0575bb3bc69aac907c91d908442e4ae6d7fe55895` |

Sky130 is the primary reported flow. Nangate45 is for finalist rank agreement
and cross-characterization sensitivity, not absolute-power claims.
