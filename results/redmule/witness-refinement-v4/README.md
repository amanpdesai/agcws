# RedMulE measured witness refinement v4

The frozen paired-edit procedure completed all 18 requests. Development qualifies
2/8 non-flat targets (alternating and ramp); confirmation qualifies 7/8 (all but
irregular). Both separate flat controls pass. Tolerance remains 0.10.

Every unresolved request exhausted its 257-slot allowance. The procedure refines
timing and job counts without inserting phases or changing matrix size/pattern;
its failures do not establish that the original requested profiles are infeasible.
No full-study admission is claimed.

`evidence.pack.json.gz` indexes the compressed evidence shards. They retain the
frozen procedure, all attempts, functional/activity evidence and `audit.json`.
The compact-evidence audit passed before packing, and the packer restored and
hash-checked all 8,785 exported files. These are RTL-activity qualification
measurements, not gate-power results or a held-out policy comparison.
