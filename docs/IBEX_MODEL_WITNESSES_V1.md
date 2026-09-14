# Ibex measured-mixture witness construction

Before executing these proposals, freeze the full generated list and its input
24-case mixture measurements. Keep the original requested bank and scale.

Per operand preset, estimate polling rate from the median last-bin rate of the
eight probes. Estimate each mixture's activity deficit per semantic operation
from its full-window transition total relative to that rate, and cycles per
operation from measured body retirement boundaries. These are approximate
construction heuristics, not claimed causal or power models.

For each target, a deterministic width-128 beam chooses one mixture per bin.
Nominal operation counts match each bin's requested deficit; beam pruning
prefers cumulative counts proportional to target deficit. Allocate exactly 4096
operations using the native Hamilton allocator. Rank final candidates by
predicted RMS error plus a fixed 1000-weight bin-overrun penalty. Retain two
per preset, each at leading idle fractions zero and one half: twelve proposals
per request, 216 total. All are charged, including duplicates and invalids.

Execute via the existing architectural reference and fixed-window evaluator,
18 parallel CPU workers, no model calls. Actual simulation alone decides
qualification at the unchanged 0.10 tolerance and nonflat floor. Preserve all
misses, do not automatically extend the search, and independently audit before
admitting witnesses. The target-guided constructor is not an agent baseline.
