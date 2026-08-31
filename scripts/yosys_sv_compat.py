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
