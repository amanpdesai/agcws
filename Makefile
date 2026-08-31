.DEFAULT_GOAL := test
PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON ?= $(VENV)/bin/python
SYNTH_DIR ?= out/aes-core-synthesis-final4
WORKLOAD ?= experiments/workloads/aes_min_scored.json
EVAL_DIR ?= out/aes-evaluation
BASELINE_DIR ?= out/aes-baseline-matrix
P_MIN ?= 128.726293
P_MAX ?= 130.431250
BUDGET ?= 200
SEEDS ?= 0
TARGETS ?= 0.10 0.25 0.50 0.75 0.90

.PHONY: test lint dev-install analysis-install verification-install chia-install chia-smoke upstream-dma-reference research-smoke inspect-liberty check-liberty-coverage synth-aes evaluate-aes determinism plot-activity temporal-search compositional-search baseline-matrix check-axi-dma-rtl run-axi-dma-rd-smoke run-axi-dma-wr-smoke run-axi-dma-workload run-axi-memory-smoke verify container-smoke
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
upstream-dma-reference:
	$(VENV_PYTHON) -m pip install -e '.[verification]'
	bash scripts/run_axi_dma_upstream_reference.sh
research-smoke:
	bash scripts/research_smoke.sh "$(SYNTH_DIR)" "$${AGCWS_ARTIFACT_ROOT:-out/research-smoke}"
lint:
	$(VENV_PYTHON) -m ruff check --select E9,F src scripts tests
inspect-liberty:
	$(VENV_PYTHON) scripts/inspect_liberty.py "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"

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
temporal-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_temporal_search.py "$(SYNTH_DIR)"
compositional-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_compositional_search.py "$(SYNTH_DIR)"
baseline-matrix:
	AGCWS_PYTHON=$(VENV_PYTHON) AGCWS_SEARCH_BUDGET=$(BUDGET) AGCWS_SEARCH_SEEDS="$(SEEDS)" \
	AGCWS_SEARCH_TARGETS="$(TARGETS)" bash scripts/run_aes_baseline_matrix.sh \
		"$(SYNTH_DIR)" "$(P_MIN)" "$(P_MAX)" "$(BASELINE_DIR)"
check-axi-dma-rtl:
	bash scripts/check_axi_dma_rtl.sh
run-axi-dma-rd-smoke:
	bash scripts/run_axi_dma_rd_smoke.sh
run-axi-dma-wr-smoke:
	bash scripts/run_axi_dma_wr_smoke.sh
run-axi-dma-workload:
	PYTHONPATH=src $(PYTHON) scripts/run_axi_dma_workload.py experiments/workloads/axi_dma_smoke.json out/axi-dma-workload
run-axi-memory-smoke:
	@mkdir -p out
	iverilog -g2012 -s agcws_axi_memory_model_smoke -o out/axi-memory-model-smoke.vvp third_party/harnesses/axi_memory_model.v third_party/harnesses/axi_memory_model_smoke.v
	(cd out && vvp axi-memory-model-smoke.vvp)
verify:
	$(MAKE) test lint check-axi-dma-rtl run-axi-memory-smoke run-axi-dma-workload
container-smoke:
	docker run --rm agcws:dev bash scripts/container_smoke.sh
