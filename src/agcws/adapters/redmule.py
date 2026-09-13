"""Timed FP16 GEMM jobs with exactly representable reference arithmetic."""

import random
import struct

from jsonschema import Draft202012Validator

from agcws.adapters.base import DesignAdapter, Validity, ValidityStage


class RedmuleTemporalAdapter(DesignAdapter):
    name = "redmule_4x4"
    useful_work_floor = 1024
    design_summary = (
        "A 4x4 floating-point accelerator executes square FP16 GEMM jobs. Matrix size "
        "changes the work per job; release phases control when sequential jobs become "
        "eligible. Late releases can miss the fixed observation deadline. The software "
        "restores accumulator inputs and checks every output after each job. Measurement "
        "includes the accelerator wrapper, not the controller CPU or testbench memories. "
        "Requested releases are earliest start times, not guaranteed completion times."
    )
    protocol_constraints = (
        "Each phase start+duration <=65536; jobs from all phases are merged by release time",
        "1..128 total jobs; size is fixed per workload at 4, 8 or 16",
        "At least 1024 multiply-accumulates must complete with all outputs correct",
        "Every requested job must complete within 65536 cycles including reset and boot",
        "Overlapping releases queue sequentially; no concurrent accelerator jobs",
    )
    workload_schema = {
        "type": "object", "additionalProperties": False,
        "required": ["size", "pattern", "data_seed", "phases"],
        "properties": {
            "size": {"type": "integer", "enum": [4, 8, 16]},
            "pattern": {"type": "string", "enum": ["zeros", "alternating", "random"]},
            "data_seed": {"type": "integer", "minimum": 0, "maximum": 65535},
            "phases": {"type": "array", "minItems": 1, "maxItems": 32,
                       "items": {"type": "object", "additionalProperties": False,
                                 "required": ["start", "duration", "jobs"], "properties": {
                                     "start": {"type": "integer", "minimum": 0, "maximum": 65535},
                                     "duration": {"type": "integer", "minimum": 1, "maximum": 65536},
                                     "jobs": {"type": "integer", "minimum": 1, "maximum": 128},
                                 }}},
        },
    }

    def validate_schema(self, workload):
        error = next(Draft202012Validator(self.workload_schema).iter_errors(workload), None)
        return Validity(False, ValidityStage.SCHEMA, error.message) if error else Validity(True)

    def validate_protocol(self, workload):
        jobs = sum(phase["jobs"] for phase in workload["phases"])
        if jobs > 128:
            return Validity(False, ValidityStage.PROTOCOL, "at most 128 jobs required")
        if any(phase["start"] + phase["duration"] > 65536 for phase in workload["phases"]):
            return Validity(False, ValidityStage.PROTOCOL, "phase extends beyond observation window")
        return Validity(True)

    def elaborate(self, workload):
        for check in (self.validate_schema, self.validate_protocol):
            validity = check(workload)
            if not validity.valid:
                raise ValueError(validity.reason)
        return sorted(phase["start"] + i * phase["duration"] // phase["jobs"]
                      for phase in workload["phases"] for i in range(phase["jobs"]))

    def useful_work(self, result):
        return result.useful_work


def reference_matrices(size, pattern, seed):
    """Entries are halves; products and all intermediate sums are exact in FP16."""
    if type(size) is not int or size not in (4, 8, 16):
        raise ValueError("supported matrix sizes are 4, 8, 16")
    if pattern not in ("zeros", "alternating", "random"):
        raise ValueError("unsupported data pattern")
    if type(seed) is not int or not 0 <= seed <= 65535:
        raise ValueError("data seed must be an integer in 0..65535")
    rng = random.Random(seed)

    def matrix(offset):
        if pattern == "zeros":
            return [0.0] * (size*size)
        if pattern == "alternating":
            return [0.5 if (i + offset) % 2 else -1.0 for i in range(size*size)]
        return [rng.choice((-1.0, -0.5, 0.0, 0.5, 1.0)) for _ in range(size*size)]

    x, w, y = matrix(0), matrix(1), matrix(2)
    z = [y[r*size+c] + sum(x[r*size+k] * w[k*size+c] for k in range(size))
         for r in range(size) for c in range(size)]
    return x, w, y, z


def stimulus_headers(workload):
    adapter = RedmuleTemporalAdapter()
    releases = adapter.elaborate(workload)
    size = workload["size"]
    matrices = reference_matrices(size, workload["pattern"], workload["data_seed"])

    def fp16(value):
        return int.from_bytes(struct.pack("<e", value), "little")

    def array(name, values, bits):
        return f"uint{bits}_t {name}[{len(values)}] = {{\n" + ", ".join(
            f"0x{value:0{bits//4}x}" for value in values) + "\n};\n"

    headers = {filename: array(name, [fp16(v) for v in values], 16)
               for filename, name, values in zip(
                   ("x_input.h", "w_input.h", "y_input.h", "z_output.h"),
                   ("x_inp", "w_inp", "y_inp", "z_oup"), matrices, strict=True)}
    z = [fp16(v) for v in matrices[3]]
    headers["golden.h"] = array("golden", [z[i] | z[i+1] << 16 for i in range(0, len(z), 2)], 32)
    headers["tensor_dim.h"] = (
        f"#define M_SIZE {size}\n#define N_SIZE {size}\n#define K_SIZE {size}\n"
        "#define SRC_FMT FP16\n#define DST_FMT FP16\n#define FPFORMAT 16\n"
    )
    headers["workload.h"] = "static const uint32_t releases[] = {" + ", ".join(map(str, releases)) + "};\n"
    return headers
