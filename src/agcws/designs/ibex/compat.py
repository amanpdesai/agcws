"""Extend the verified SKY130 models to Ibex's unreset enabled flip-flops."""

import re

from agcws.designs.redmule.compat import functional_primitives as base_primitives


def functional_primitives(source):
    text = base_primitives(source)
    name = 'sky130_fd_sc_hd__udp_dff$P'
    pattern = r'primitive ' + re.escape(name) + r'\s*\(.*?endprimitive'
    replacement = f'''module {name} (output reg Q, input D, CLK);
  always @(posedge CLK) Q <= D;
endmodule'''
    text, count = re.subn(pattern, replacement, text, flags=re.S)
    if count != 1:
        raise ValueError('expected exactly one unreset SKY130 DFF primitive')
    return text
