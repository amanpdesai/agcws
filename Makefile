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
VENV ?= .venv
VENV_PYTHON ?= $(VENV)/bin/python
SYNTH_DIR ?= out/aes-core-synthesis-final4
WORKLOAD ?= experiments/workloads/aes_min_scored.json
EVAL_DIR ?= out/aes-evaluation
BASELINE_DIR ?= out/aes-baseline-matrix-complete
ANALYSIS_DIR ?= out/aes-baseline-analysis
CORPUS_DIR ?= out/aes-random-corpus
TEMPORAL_CORPUS_DIR ?= out/aes-temporal-corpus
CROSS_PDK_DIR ?= out/aes-cross-pdk
PDK_VALIDATION_CORPUS ?= out/aes-pdk-rank-20260831/corpus
PDK_VALIDATION_DIR ?= out/aes-pdk-rank-20260831
DMA_CROSS_PDK_DIR ?= out/axi-dma-cross-pdk
DMA_POLICIES ?= random,mutation,evolutionary,one-shot-agent,offline-hybrid
DMA_SEARCH_DIR ?= out/axi-dma-search
IBEX_MATRIX_ROOT ?= out/ibex-matrix
IBEX_CALIBRATION ?= out/ibex-activity-calibration/calibration.json
DMA_P_MIN ?= 19.674030658250675
DMA_P_MAX ?= 19.80286241920591
DMA_INFERENCE_ROOTS ?= out/axi-dma-matrix-calibrated-200-seed0 out/axi-dma-matrix-calibrated-200-seed1 out/axi-dma-matrix-calibrated-200-seed2 out/axi-dma-matrix-calibrated-200-seed3 out/axi-dma-matrix-calibrated-200-seed4
DMA_CALIBRATION_ROOTS ?= out/axi-dma-calibration-seed1-fixed2 out/axi-dma-calibration-seed2 out/axi-dma-calibration-seed3
TEMPORAL_PILOT_ROOTS ?= out/aes-temporal-heldout-20260901-seed0-32 out/aes-temporal-heldout-20260901-seed1 out/aes-temporal-heldout-20260901-seed2-32 out/aes-temporal-burst-seed0 out/aes-temporal-burst-seed1 out/aes-temporal-burst-seed2 out/aes-temporal-target2-seed0 out/aes-temporal-target2-seed1 out/aes-temporal-target2-seed2 out/aes-temporal-target3-seed0 out/aes-temporal-target3-seed1 out/aes-temporal-target3-seed2
COMPOSITIONAL_PILOT_ROOTS ?= out/aes-compositional-heldout-20260901-seed0-32 out/aes-compositional-heldout-20260901-seed1 out/aes-compositional-heldout-20260901-seed2-32 out/aes-compositional-target1-seed0 out/aes-compositional-target1-seed1 out/aes-compositional-target1-seed2 out/aes-compositional-target2-seed0 out/aes-compositional-target2-seed1 out/aes-compositional-target2-seed2 out/aes-compositional-target3-seed0 out/aes-compositional-target3-seed1 out/aes-compositional-target3-seed2 out/aes-compositional-target4-seed0 out/aes-compositional-target4-seed1 out/aes-compositional-target4-seed2
TEMPORAL_POLICY_MATRIX_ROOT ?= out/aes-temporal-policy-matrix-20260901-v2
COMPOSITIONAL_POLICY_MATRIX_ROOT ?= out/aes-compositional-policy-matrix-20260901-v2
COMPOSITIONAL_FULL_POLICY_MATRIX_ROOT ?= out/aes-compositional-policy-matrix-20260901-300
FINALIST_TRIALS ?= $(BASELINE_DIR)/target-0.50/seed-0/random/trials.jsonl
WAVEFORM ?= $(EVAL_DIR)/activity.vcd
DMA_WAVEFORM ?= out/axi-dma-coupled/activity.vcd
P_MIN ?= 128.726293
P_MAX ?= 130.431250
CALIBRATION ?= experiments/calibration/aes_activity_calibration.json
BUDGET ?= 200
SEEDS ?= 0
TARGETS ?= 0.10 0.25 0.50 0.75 0.90
IBEX_CORE ?= lowrisc:ibex:ibex_simple_system
IBEX_SOURCES ?= $(if $(AGCWS_ARTIFACT_ROOT),$(AGCWS_ARTIFACT_ROOT),out)/ibex-sources/sources.json
IBEX_TOP ?= ibex_top

.PHONY: test lint dev-install analysis-install verification-install chia-install chia-smoke chia-node-smoke upstream-dma-reference research-smoke research-audit audit-reproducibility audit-profile-matrix audit-temporal-profile-matrix vertex-preflight verify-artifact inspect-liberty inspect-liberties check-liberty-coverage synth-aes evaluate-aes determinism plot-activity plot-search-curves plot-temporal-policy-matrix plot-compositional-policy-matrix analyze-baseline random-corpus temporal-corpus temporal-search compositional-search baseline-matrix cross-pdk run-aes-pdk-corpus validate-aes-pdk-corpus validate-finalists cross-pdk-dma axi-dma-search aggregate-axi-dma-calibration infer-dma infer-temporal-policy-matrix infer-compositional-policy-matrix aggregate-temporal-pilot aggregate-compositional-pilot aggregate-temporal-policy-matrix aggregate-compositional-policy-matrix validate-axi-dma-finalists check-axi-dma-rtl run-axi-dma-rd-smoke run-axi-dma-wr-smoke run-axi-dma-workload run-axi-dma-coupled run-axi-memory-smoke inventory-memories memory-collateral audit-memory-collateral compile-ibex resolve-ibex-sources probe-ibex-synthesis synthesize-ibex-core check-ibex-rtl run-ibex verify-ibex ibex-search aggregate-ibex infer-ibex verify container-smoke
test:
	$(VENV_PYTHON) -m pytest -q
dev-install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e '.[dev]'
analysis-install:
	$(VENV_PYTHON) -m pip install -e '.[analysis]'
verification-install:
	$(VENV_PYTHON) -m pip install -e '.[verification]'
chia-install:
	$(VENV_PYTHON) -m pip install -e '.[chia]'
	$(VENV_PYTHON) -m pip install -e tools/chia
chia-smoke:
	$(VENV_PYTHON) scripts/chia_smoke.py
chia-node-smoke:
	PYTHONPATH=src $(VENV_PYTHON) scripts/chia_node_smoke.py
upstream-dma-reference:
	$(VENV_PYTHON) -m pip install -e '.[verification]'
	bash scripts/run_axi_dma_upstream_reference.sh "$${AGCWS_ARTIFACT_ROOT:-out}/axi-dma-upstream-reference"
research-smoke:
	AGCWS_PYTHON=$(VENV_PYTHON) bash scripts/research_smoke.sh "$(SYNTH_DIR)" "$${AGCWS_ARTIFACT_ROOT:-out/research-smoke}"
research-audit:
	$(MAKE) test lint chia-smoke chia-node-smoke inspect-liberties audit-reproducibility verify-artifact validate-aes-pdk-corpus audit-compositional-full-policy-matrix audit-temporal-profile-matrix check-axi-dma-rtl run-axi-memory-smoke run-axi-dma-workload
audit-reproducibility:
	$(VENV_PYTHON) scripts/audit_reproducibility.py
vertex-preflight:
	$(VENV_PYTHON) scripts/vertex_preflight.py
verify-artifact:
	$(VENV_PYTHON) scripts/verify_artifact.py "$${AGCWS_ARTIFACT:-$(EVAL_DIR)}"
lint:
	$(VENV_PYTHON) -m ruff check --select E9,F src scripts tests
inspect-liberty:
	$(VENV_PYTHON) scripts/inspect_liberty.py "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
inspect-liberties:
	$(VENV_PYTHON) scripts/inspect_liberty.py "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
	$(VENV_PYTHON) scripts/inspect_liberty.py "$${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}"

check-liberty-coverage:
	$(VENV_PYTHON) scripts/check_liberty_coverage.py out/aes-core-synthesis-final4/stat.json "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
synth-aes:
	bash scripts/synthesize_aes_core.sh "$(SYNTH_DIR)"
evaluate-aes:
	PYTHONPATH=src $(VENV_PYTHON) scripts/evaluate_aes_workload.py "$(WORKLOAD)" "$(SYNTH_DIR)" --out "$(EVAL_DIR)"
determinism:
	PYTHONPATH=src $(VENV_PYTHON) scripts/check_aes_determinism.py "$(WORKLOAD)" "$(SYNTH_DIR)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-determinism"
plot-activity:
	$(VENV_PYTHON) analysis/plot_activity.py "$(EVAL_DIR)/activity.json" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/activity.png"
plot-search-curves:
	$(VENV_PYTHON) analysis/plot_search_curves.py "$(BASELINE_DIR)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/search-curves.png"
plot-temporal-policy-matrix:
	$(VENV_PYTHON) analysis/plot_search_curves.py "$(TEMPORAL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/temporal-policy-convergence.png"
plot-compositional-policy-matrix:
	$(VENV_PYTHON) analysis/plot_search_curves.py "$(COMPOSITIONAL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/compositional-policy-convergence.png"
plot-compositional-full-policy-matrix:
	$(VENV_PYTHON) analysis/plot_search_curves.py "$(COMPOSITIONAL_FULL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/compositional-policy-convergence-300.png"
analyze-baseline:
	@mkdir -p "$(ANALYSIS_DIR)"
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py "$(BASELINE_DIR)" --out "$(ANALYSIS_DIR)/aggregate.json"
	$(VENV_PYTHON) analysis/plot_search_curves.py "$(BASELINE_DIR)" --out "$(ANALYSIS_DIR)/convergence.png"
random-corpus:
	PYTHONPATH=src $(VENV_PYTHON) scripts/run_aes_random_corpus.py "$(SYNTH_DIR)" --out "$(CORPUS_DIR)"
temporal-corpus:
	PYTHONPATH=src $(VENV_PYTHON) scripts/run_aes_temporal_corpus.py "$(SYNTH_DIR)" --out "$(TEMPORAL_CORPUS_DIR)"
temporal-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_temporal_search.py "$(SYNTH_DIR)"
compositional-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_compositional_search.py "$(SYNTH_DIR)"
baseline-matrix:
	AGCWS_PYTHON=$(VENV_PYTHON) AGCWS_SEARCH_BUDGET=$(BUDGET) AGCWS_SEARCH_SEEDS="$(SEEDS)" \
	AGCWS_SEARCH_TARGETS="$(TARGETS)" AGCWS_CALIBRATION="$(CALIBRATION)" bash scripts/run_aes_baseline_matrix.sh \
		"$(SYNTH_DIR)" "$(P_MIN)" "$(P_MAX)" "$(BASELINE_DIR)"
cross-pdk:
	bash scripts/run_aes_cross_pdk.sh "$(WAVEFORM)" "$(CROSS_PDK_DIR)"
validate-aes-pdk-corpus:
	$(VENV_PYTHON) scripts/validate_aes_pdk_corpus.py "$(PDK_VALIDATION_CORPUS)" \
		"$(PDK_VALIDATION_DIR)/sky-reports" "$(PDK_VALIDATION_DIR)/nangate-reports" \
		--out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-pdk-corpus-validation.json"
run-aes-pdk-corpus:
	bash scripts/run_aes_pdk_corpus.sh "$(CORPUS_DIR)" "$(CROSS_PDK_DIR)" \
		"$${AGCWS_ARTIFACT_ROOT:-out}/aes-pdk-corpus"
cross-pdk-dma:
	@test -f "$(DMA_WAVEFORM)" || (echo "missing DMA_WAVEFORM=$(DMA_WAVEFORM)" >&2; exit 1)
	bash scripts/run_axi_dma_cross_pdk.sh "$(DMA_WAVEFORM)" "$(DMA_CROSS_PDK_DIR)"
axi-dma-search:
	PYTHONPATH=src $(VENV_PYTHON) scripts/run_axi_dma_search.py --policies "$(DMA_POLICIES)" --budget "$(BUDGET)" --p-min "$(DMA_P_MIN)" --p-max "$(DMA_P_MAX)" --out "$(DMA_SEARCH_DIR)"
aggregate-axi-dma-calibration:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_axi_dma_calibration.py $(DMA_CALIBRATION_ROOTS) --out "$${AGCWS_ARTIFACT_ROOT:-out}/axi-dma-calibration.json"
infer-dma:
	PYTHONPATH=src $(VENV_PYTHON) scripts/infer_policy_comparisons.py $(DMA_INFERENCE_ROOTS) --out "$${AGCWS_ARTIFACT_ROOT:-out}/axi-dma-inference.json"
infer-temporal-policy-matrix:
	PYTHONPATH=src $(VENV_PYTHON) scripts/infer_policy_comparisons.py "$(TEMPORAL_POLICY_MATRIX_ROOT)" --baseline random --metric auc_best_so_far --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-temporal-policy-inference-32.json"
infer-compositional-policy-matrix:
	PYTHONPATH=src $(VENV_PYTHON) scripts/infer_policy_comparisons.py "$(COMPOSITIONAL_FULL_POLICY_MATRIX_ROOT)" --baseline random --metric auc_best_so_far --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-compositional-policy-inference-300.json"
aggregate-temporal-pilot:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py $(TEMPORAL_PILOT_ROOTS) --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-temporal-pilot-aggregate.json"
aggregate-compositional-pilot:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py $(COMPOSITIONAL_PILOT_ROOTS) --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-compositional-pilot-aggregate.json"
aggregate-temporal-policy-matrix:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py "$(TEMPORAL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-temporal-policy-matrix-20260901-v2-aggregate.json"
aggregate-compositional-policy-matrix:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py "$(COMPOSITIONAL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-compositional-policy-matrix-20260901-v2-aggregate.json"
aggregate-compositional-full-policy-matrix:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py "$(COMPOSITIONAL_FULL_POLICY_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-compositional-policy-matrix-20260901-300-aggregate.json"
audit-profile-matrix:
	$(VENV_PYTHON) scripts/audit_profile_matrix.py out/aes-compositional-targets.json out/aes-compositional-policy-matrix-20260901-v2-aggregate.json --policies random mutation evolutionary offline-agent one-shot-agent --seeds 3 --budget 32
audit-compositional-full-policy-matrix:
	$(VENV_PYTHON) scripts/audit_profile_matrix.py out/aes-compositional-targets.json out/aes-compositional-policy-matrix-20260901-300-aggregate.json --policies random mutation evolutionary offline-agent one-shot-agent --seeds 3 --budget 300
audit-temporal-profile-matrix:
	$(VENV_PYTHON) scripts/audit_profile_matrix.py out/aes-temporal-targets-2.json out/aes-temporal-targets-4.json out/aes-temporal-policy-matrix-20260901-v2-aggregate.json --policies random mutation evolutionary offline-agent one-shot-agent --seeds 3 --budget 32
validate-axi-dma-finalists:
	PYTHONPATH=src $(VENV_PYTHON) scripts/validate_axi_dma_finalists.py "$${DMA_FINALIST_TRIALS:-out/axi-dma-search/trials.jsonl}" "$${DMA_SYNTH_DIR:-out/axi-dma-synthesis-sky130-v2}" --out "$${AGCWS_ARTIFACT_ROOT:-out}/axi-dma-finalist-validation"
validate-finalists:
	@test -f "$(FINALIST_TRIALS)" || (echo "missing FINALIST_TRIALS=$(FINALIST_TRIALS)" >&2; exit 1)
	PYTHONPATH=src $(VENV_PYTHON) scripts/validate_finalists.py "$(FINALIST_TRIALS)" "$(SYNTH_DIR)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/finalist-validation"
check-axi-dma-rtl:
	bash scripts/check_axi_dma_rtl.sh
run-axi-dma-rd-smoke:
	bash scripts/run_axi_dma_rd_smoke.sh
run-axi-dma-wr-smoke:
	bash scripts/run_axi_dma_wr_smoke.sh
run-axi-dma-workload:
	PYTHONPATH=src $(VENV_PYTHON) scripts/run_axi_dma_workload.py experiments/workloads/axi_dma_smoke.json out/axi-dma-workload
run-axi-dma-coupled:
	AGCWS_PYTHON=$(VENV_PYTHON) bash scripts/run_axi_dma_coupled.sh experiments/workloads/axi_dma_smoke.json out/axi-dma-coupled
run-axi-memory-smoke:
	@mkdir -p out
	$${AGCWS_IVERILOG:-iverilog} -g2012 -s agcws_axi_memory_model_smoke -o out/axi-memory-model-smoke.vvp third_party/harnesses/axi_memory_model.v third_party/harnesses/axi_memory_model_smoke.v
	(cd out && vvp axi-memory-model-smoke.vvp)
audit-memory-collateral:
	@test -n "$(MEMORY_COLLATERAL)" || (echo "set MEMORY_COLLATERAL" >&2; exit 2)
	$(VENV_PYTHON) scripts/audit_memory_collateral.py "$(MEMORY_COLLATERAL)"
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
synthesize-ibex-core:
	@test "$(IBEX_TOP)" = "ibex_core" || (echo "use IBEX_TOP=ibex_core for this target" >&2; exit 2)
	@root="$${AGCWS_ARTIFACT_ROOT:-out}/ibex-core-sources"; \
	PYTHONPATH=src $(VENV_PYTHON) scripts/resolve_ibex_sources.py --core lowrisc:ibex:ibex_core --out "$$root" >/dev/null; \
	sources="$$root/sources.json"; \
	PYTHONPATH=src $(VENV_PYTHON) scripts/probe_ibex_synthesis.py "$$sources" --top "$(IBEX_TOP)" --map --out "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-core-synthesis"
check-ibex-rtl: resolve-ibex-sources
	PYTHONPATH=src $(VENV_PYTHON) scripts/check_ibex_verilator.py "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-sources/sources.json"
run-ibex:
	# Defaults: "$${AGCWS_ARTIFACT_ROOT:-out}/ibex" or
	# "$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}".
	ibex_root="$${AGCWS_IBEX_ARTIFACT_ROOT:-$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}}"; \
	$(VENV_PYTHON) scripts/generate_ibex_workload.py "$$ibex_root/floor_workload.json"; \
	bash scripts/run_ibex_workload.sh "$$ibex_root/floor_workload.json" "$$ibex_root"
verify-ibex: run-ibex
	ibex_root="$${AGCWS_IBEX_ARTIFACT_ROOT:-$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}}"; \
	$(VENV_PYTHON) scripts/verify_artifact.py --require-activity "$$ibex_root"
ibex-search:
	@test -f "$(IBEX_CALIBRATION)" || (echo "run calibrate_ibex_activity.py first or set IBEX_CALIBRATION" >&2; exit 2)
	PYTHONPATH=src $(VENV_PYTHON) scripts/run_ibex_search.py --calibration "$(IBEX_CALIBRATION)" --budget "$(BUDGET)" --seed "$(SEEDS)" --out "$(IBEX_MATRIX_ROOT)"
aggregate-ibex:
	PYTHONPATH=src $(VENV_PYTHON) scripts/aggregate_runs.py "$(IBEX_MATRIX_ROOT)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-matrix-aggregate.json"
infer-ibex:
	PYTHONPATH=src $(VENV_PYTHON) scripts/infer_policy_comparisons.py "$(IBEX_MATRIX_ROOT)" --baseline random --metric auc_best_so_far --out "$${AGCWS_ARTIFACT_ROOT:-out}/ibex-matrix-inference.json"
verify:
	$(MAKE) test lint audit-reproducibility verify-artifact validate-aes-pdk-corpus check-axi-dma-rtl run-axi-memory-smoke run-axi-dma-workload
container-smoke:
	docker run --rm agcws:dev bash scripts/container_smoke.sh
