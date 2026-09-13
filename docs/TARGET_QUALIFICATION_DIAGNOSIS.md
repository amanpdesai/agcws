# Qualification diagnosis and next implementation gate

This is readiness engineering, not a policy comparison or a revision of the
frozen [v1 procedure](TARGET_QUALIFICATION_V1.md). Failures remain in the evidence.

## Observed gaps

- AES/DMA: fixed useful work and idle budget constrain the mean. Two requested
  shape families fail the necessary non-flatness floor before witness search.
- Mesh: the completed searches qualify 6/8 development and 5/8 confirmation
  requests. A wide calibration envelope alone does not establish reachability
  of an arbitrary eight-bin vector.
- RedMulE: 0/8 development and 1/8 confirmation requests qualify. Inspecting
  selected trajectories shows substantial requested/achieved rate differences,
  not just near-threshold misses. Matrix size changes both activity and job
  duration. Release times are requests to a sequential worker, not guarantees
  that a job starts or completes in its requested bin.
- Ibex: searches are still running. Do not diagnose their outcome prematurely.

These observations do not prove physical infeasibility. The current search is
bounded and the random generator does not cover all legal schedules uniformly.
Conversely, adding search budget without understanding job duration could waste
time on impossible waveforms.

## Next slice

1. Preserve v1 manifests, all attempted requests and complete witness archives.
   Keep running measurement code unchanged until the in-flight studies finish.
2. Measure temporal control directly in a separate, predeclared CPU probe:
   job duration, idle rate, sustained rate, release-to-start delay, completion
   and per-bin work. For RedMulE, stratify by supported matrix size and pattern;
   for fixed-work AES/DMA, inspect the achievable duty cycle under their actual
   work/window contract. Retain failed probes, not just attractive profiles.
3. Use those measurements to distinguish contract limitations from search
   limitations. Define a v2 qualification procedure before executing its search.
   A stronger witness optimizer must optimize the frozen analytic request, not
   replace it with its achieved waveform. If a measurement contract changes,
   recalibrate and give it a new fingerprint; old results remain v1.
4. Preserve eight substantive non-flat families plus the separate control per
   design. Do not lower admission thresholds simply to fill the quota. Record
   family distances, constant-vector floors and every qualification failure.
5. Only qualified banks advance to bounded Flash and matched baseline smokes.
   Hidden witnesses and probe programs are not agent context. Exposing a new
   schedule tool requires equal access for the classical policies.

The probe configuration and v2 search budget are not frozen by this note. They
must be specified and tested before those measurements begin. No new paid panel
is authorized by this diagnosis.
