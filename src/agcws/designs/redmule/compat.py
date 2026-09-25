"""Audited two-state Verilator equivalents of six pinned SKY130 UDPs.

The original source/license is retained. These implement the known-input state
transitions used by Verilator, not a claim of four-state UDP equivalence. Icarus
regressions compare against the original tables, including sequential hold/reset.
"""

import hashlib
import re

PRIMITIVES_SHA256 = "81351b44f54dd9b5e3cd07a845cbe9d90e889d29edfcbff57a527280839bbccc"
MODELS = {
    "udp_dff$PR": """(output reg Q, input D, CLK, RESET);
  always @(posedge CLK or posedge RESET) if (RESET) Q <= 0; else Q <= D;
endmodule""",
    "udp_dff$PS": """(output reg Q, input D, CLK, SET);
  always @(posedge CLK or posedge SET) if (SET) Q <= 1; else Q <= D;
endmodule""",
    "udp_dlatch$P": """(output reg Q, input D, GATE);
  always @* if (GATE) Q = D;
endmodule""",
    "udp_mux_2to1": """(output X, input A0, A1, S);
  assign X = S ? A1 : A0;
endmodule""",
    "udp_mux_2to1_N": """(output Y, input A0, A1, S);
  assign Y = ~(S ? A1 : A0);
endmodule""",
    "udp_mux_4to2": """(output X, input A0, A1, A2, A3, S0, S1);
  assign X = S1 ? (S0 ? A3 : A2) : (S0 ? A1 : A0);
endmodule""",
}


def functional_primitives(source):
    if hashlib.sha256(source).hexdigest() != PRIMITIVES_SHA256:
        raise ValueError("unsupported SKY130 primitive revision; equivalence regression required")
    text = source.decode()
    for short, body in MODELS.items():
        name = "sky130_fd_sc_hd__" + short
        pattern = r"primitive " + re.escape(name) + r"\s*\(.*?endprimitive"
        text, count = re.subn(pattern, "module " + name + " " + body, text, flags=re.S)
        if count != 1:
            raise ValueError(f"expected exactly one primitive: {name}")
    return text
