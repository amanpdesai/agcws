# Ibex division/ALU mixture diagnostic

All 24 frozen eight-instruction body variants passed functional checks: three
operand presets times one through eight divisions, with XORs in the remaining
positions. Each executes the unchanged 4096 semantic operations in the same
200000-cycle window. `summary.json` records measured body timing and bin rates;
`evidence/` preserves all measurements, functional checks and execution records.

These measurements feed the separately frozen modeled-witness constructor.
They are not a target-qualification result, policy comparison or gate-power
measurement. The constructor's predicted rates cannot admit a witness; only
its later actual simulation and independent audit can do that.
