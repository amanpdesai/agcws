#!/usr/bin/env python3
"""Create a deterministic Yosys-frontend compatibility copy of SV sources."""
from __future__ import annotations

import re
import sys
from pathlib import Path

FUNCTION = re.compile(
    r"(?P<head>function\b(?:(?!endfunction).)*?\b(?P<name>[A-Za-z_$][\w$]*)\s*\([^;]*?\);)(?P<body>.*?)(?P<end>endfunction)",
    re.DOTALL,
)


def transform(text: str) -> str:
    def function_body(match: re.Match[str]) -> str:
        body = re.sub(r"\breturn\s+([^;]+);", rf"{match.group('name')} = \1;", match.group("body"))
        return match.group("head") + body + match.group("end")

    text = FUNCTION.sub(function_body, text)
    # Yosys treats ``shift`` as a token in this older frontend, while the
    # OpenTitan package uses it as a legal function argument name.
    text = re.sub(
        r"(function\s+automatic\s+logic\s+\[31:0\]\s+aes_circ_byte_shift\([^;]*?\[1:0\])\s+shift(\);.*?endfunction)",
        r"\1 shift_amt\2",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"(function\s+automatic\s+logic\s+\[31:0\]\s+aes_circ_byte_shift.*?endfunction)",
        lambda match: re.sub(r"\bshift\b", "shift_amt", match.group(1)),
        text,
        flags=re.DOTALL,
    )
    # The stock Yosys frontend cannot parse OpenTitan's packed 4x4x8-byte
    # function signature. Preserve the equivalent 128-bit permutation in the
    # compatibility copy; packed SV values have the same total width.
    text = re.sub(
        r"function automatic logic \[3:0\]\[3:0\]\[7:0\] aes_transpose\(.*?endfunction",
        """function automatic logic [127:0] aes_transpose(input logic [127:0] in);
  logic [127:0] transpose;
  integer i;
  integer j;
  begin
    transpose = '0;
    for (i = 0; i < 4; i = i + 1)
      for (j = 0; j < 4; j = j + 1)
        transpose[8*(15-4*i-j) +: 8] = in[8*(15-4*j-i) +: 8];
    aes_transpose = transpose;
  end
endfunction""",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"function automatic logic \[3:0\]\[7:0\] aes_col_get\(.*?endfunction",
        """function automatic logic [31:0] aes_col_get(input logic [127:0] in, input logic [1:0] idx);
  integer i;
  begin
    for (i = 0; i < 4; i = i + 1)
      aes_col_get[8*i +: 8] = in[8*(15-4*i-idx) +: 8];
  end
endfunction""",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"\b(?:GCMDegree|prs_rate_e|key_len_e|aes_mode_e|aes_op_e)'\(([^()]*)\)", r"\1", text)
    text = re.sub(
        r"parameter ctrl_reg_t CTRL_RESET = '\{.*?^};$",
        "parameter ctrl_reg_t CTRL_RESET = '0;",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    return text


if __name__ == "__main__":
    source, target = map(Path, sys.argv[1:3])
    target.write_text(transform(source.read_text(errors="replace")))
