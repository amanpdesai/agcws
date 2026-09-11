.DEFAULT_GOAL := test
-include .env

# Keep host-specific tool paths in .env while exporting them to scripts.  The
# file is intentionally ignored; .env.example is the portable contract.
export AGCWS_VERILATOR AGCWS_YOSYS AGCWS_OPENSTA AGCWS_VCD2SAIF AGCWS_IVERILOG
export AGCWS_VVP AGCWS_IVERILOG_VPI AGCWS_FST2VCD AGCWS_MYHDL_DIR
export AGCWS_FUSESOC AGCWS_RISCV_GCC AGCWS_RISCV_OBJCOPY AGCWS_IBEX_ROOT AGCWS_IBEX_SIM
export AGCWS_SLANG_PLUGIN AGCWS_MEMORY_LIBMAP AGCWS_LIBERTY AGCWS_LIBERTY_NANGATE45
export AGCWS_ARTIFACT_ROOT AGCWS_PROFILE_SMOKE_BUDGET AGCWS_CALIBRATION
export AGCWS_GCP_PROJECT AGCWS_GEMINI_MODEL

# Portable defaults keep an absent .env from exporting empty executable names.
ifeq ($(strip $(AGCWS_VERILATOR)),)
AGCWS_VERILATOR := verilator
endif
ifeq ($(strip $(AGCWS_YOSYS)),)
AGCWS_YOSYS := yosys
endif
ifeq ($(strip $(AGCWS_OPENSTA)),)
AGCWS_OPENSTA := sta
endif
ifeq ($(strip $(AGCWS_VCD2SAIF)),)
AGCWS_VCD2SAIF := vcd2saif
endif
ifeq ($(strip $(AGCWS_IVERILOG)),)
AGCWS_IVERILOG := iverilog
endif
ifeq ($(strip $(AGCWS_VVP)),)
AGCWS_VVP := vvp
endif
ifeq ($(strip $(AGCWS_IVERILOG_VPI)),)
AGCWS_IVERILOG_VPI := iverilog-vpi
endif
ifeq ($(strip $(AGCWS_FST2VCD)),)
AGCWS_FST2VCD := fst2vcd
endif
ifeq ($(strip $(AGCWS_FUSESOC)),)
AGCWS_FUSESOC := fusesoc
endif
ifeq ($(strip $(AGCWS_RISCV_GCC)),)
AGCWS_RISCV_GCC := riscv64-unknown-elf-gcc
endif
ifeq ($(strip $(AGCWS_RISCV_OBJCOPY)),)
AGCWS_RISCV_OBJCOPY := riscv64-unknown-elf-objcopy
endif
ifeq ($(strip $(AGCWS_ARTIFACT_ROOT)),)
AGCWS_ARTIFACT_ROOT := out
endif
PYTHON ?= python3
VENV_PYTHON ?= .venv/bin/python
PIPELINE = PYTHONPATH=src $(VENV_PYTHON) -m agcws.pipeline

.PHONY: test lint install archive-check archive-audit pipeline-help vertex-preflight container-build container-prune
install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -e '.[dev,research,analysis]'
test:
	$(VENV_PYTHON) -m pytest -q
lint:
	$(VENV_PYTHON) -m ruff check src tests scripts analysis validation maintenance flows
archive-check:
	$(PIPELINE) archive-check
archive-audit:
	$(PIPELINE) archive-audit
pipeline-help:
	$(PIPELINE) --help
vertex-preflight:
	$(VENV_PYTHON) scripts/vertex_preflight.py
container-build:
	bash docker/build.sh
container-prune:
	bash docker/prune.sh
chia-install:
	$(VENV_PYTHON) -m pip install -e tools/chia
chia-smoke:
	$(VENV_PYTHON) scripts/chia_smoke.py
chia-node-smoke:
	$(VENV_PYTHON) scripts/chia_node_smoke.py
inspect-liberties:
	$(VENV_PYTHON) scripts/inspect_liberty.py "$(AGCWS_LIBERTY)"
	$(VENV_PYTHON) scripts/inspect_liberty.py "$(AGCWS_LIBERTY_NANGATE45)"

EVAL_DIR ?= out/aes-evaluation
IBEX_CORE ?= lowrisc:ibex:ibex_simple_system
IBEX_SOURCES ?= $(if $(AGCWS_ARTIFACT_ROOT),$(AGCWS_ARTIFACT_ROOT),out)/ibex-sources/sources.json
IBEX_TOP ?= ibex_top
SYNTH_DIR ?= out/aes-core-synthesis-final4
VENV ?= .venv
WORKLOAD ?= experiments/workloads/aes_min_scored.json

audit-reproducibility:
	$(VENV_PYTHON) scripts/audit_reproducibility.py

synth-aes:
	bash scripts/synthesize_aes_core.sh "$(SYNTH_DIR)"

evaluate-aes:
	PYTHONPATH=src $(VENV_PYTHON) scripts/evaluate_aes_workload.py "$(WORKLOAD)" "$(SYNTH_DIR)" --out "$(EVAL_DIR)"

audit-memory-collateral:
	@test -n "$(MEMORY_COLLATERAL)" || (echo "set MEMORY_COLLATERAL" >&2; exit 2)
	$(VENV_PYTHON) scripts/audit_memory_collateral.py "$(MEMORY_COLLATERAL)"

audit-memory-collateral-all:
	@set -e; for top in aes axi_dma ibex_core; do \
		$(VENV_PYTHON) scripts/audit_memory_collateral.py "$${AGCWS_ARTIFACT_ROOT:-out}/memory-collateral/$$top"; \
	done

inventory-memories:
	@test -n "$(MEMORY_TOP)" -a -n "$(MEMORY_SOURCE)" || (echo "set MEMORY_TOP and MEMORY_SOURCE" >&2; exit 2)
	$(VENV_PYTHON) scripts/inventory_yosys_memories.py --top "$(MEMORY_TOP)" --source "$(MEMORY_SOURCE)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/memory-inventory/$(MEMORY_TOP).json"

memory-collateral:
	@test -n "$(MEMORY_TOP)" -a -f "$(MEMORY_INVENTORY)" || (echo "set MEMORY_TOP and MEMORY_INVENTORY" >&2; exit 2)
	$(VENV_PYTHON) scripts/generate_memory_collateral.py "$(MEMORY_INVENTORY)" "$${AGCWS_ARTIFACT_ROOT:-out}/memory-collateral/$(MEMORY_TOP)"

compile-ibex:
	PYTHONPATH=src $(VENV_PYTHON) scripts/compile_ibex_workload.py experiments/workloads/ibex_smoke.json out/ibex/ibex_smoke.elf

resolve-ibex-sources:
	PYTHONPATH=src $(VENV_PYTHON) scripts/resolve_ibex_sources.py --core "$(IBEX_CORE)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-sources"

probe-ibex-synthesis:
	PYTHONPATH=src $(VENV_PYTHON) scripts/probe_ibex_synthesis.py "$(IBEX_SOURCES)" --top "$(IBEX_TOP)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-synthesis-probe"

check-ibex-rtl: resolve-ibex-sources
	PYTHONPATH=src $(VENV_PYTHON) scripts/check_ibex_verilator.py "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-sources/sources.json"

run-ibex:
	# Defaults: "$${AGCWS_ARTIFACT_ROOT:-out}/ibex" or
	# "$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}".
	ibex_root="$${AGCWS_IBEX_ARTIFACT_ROOT:-$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}}"; \
	$(VENV_PYTHON) scripts/generate_ibex_workload.py "$$ibex_root/floor_workload.json"; \
	bash scripts/run_ibex_workload.sh "$$ibex_root/floor_workload.json" "$$ibex_root"

container-smoke:
	docker run --rm agcws:dev bash scripts/container_smoke.sh
