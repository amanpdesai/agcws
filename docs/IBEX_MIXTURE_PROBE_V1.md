# Ibex mixed-body characterization

The completed 88-case diagnostic identifies division operands as an important
activity control. Before constructing new witnesses, characterize the missing
intermediate rates: bodies of eight instructions, with one through eight
divisions and the remaining instructions XORs. All operations read registers
zero/one and write register seven, preserving their inputs. Use three fixed
operand presets already measured in the first probe (ones, large numerator /
small denominator, and alternating bits). One release-zero segment, unchanged
4096 operations and 200000-cycle observation window: 24 fixed cases total.

Freeze before execution; 18 parallel CPU workers, no model calls. Preserve all
failures. Measure actual body execution durations and activity for subsequent
explicit target-guided allocation, rather than assuming instruction latencies.
This step does not admit targets, revise the bank or establish infeasibility.
