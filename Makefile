.DEFAULT_GOAL := test
PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON ?= $(VENV)/bin/python
SYNTH_DIR ?= out/aes-core-synthesis
WORKLOAD ?= experiments/workloads/aes_min_scored.json
EVAL_DIR ?= out/aes-evaluation

.PHONY: test lint dev-install inspect-liberty check-liberty-coverage synth-aes evaluate-aes determinism plot-activity temporal-search compositional-search check-axi-dma-rtl run-axi-dma-rd-smoke run-axi-dma-wr-smoke run-axi-dma-workload container-smoke
test:
	$(PYTHON) -m pytest -q
dev-install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e '.[dev]'
lint:
	$(PYTHON) -m ruff check --select E9,F src scripts tests
inspect-liberty:
	$(PYTHON) scripts/inspect_liberty.py "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"

check-liberty-coverage:
	$(PYTHON) scripts/check_liberty_coverage.py out/aes-core-synthesis-final4/stat.json "$${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
synth-aes:
	bash scripts/synthesize_aes_core.sh "$(SYNTH_DIR)"
evaluate-aes:
	PYTHONPATH=src $(PYTHON) scripts/evaluate_aes_workload.py "$(WORKLOAD)" "$(SYNTH_DIR)" --out "$(EVAL_DIR)"
determinism:
	PYTHONPATH=src $(PYTHON) scripts/check_aes_determinism.py "$(WORKLOAD)" "$(SYNTH_DIR)" --out "$${AGCWS_ARTIFACT_ROOT:-out}/aes-determinism"
plot-activity:
	$(PYTHON) analysis/plot_activity.py "$(EVAL_DIR)/activity.json" --out "$${AGCWS_ARTIFACT_ROOT:-out}/figures/activity.png"
temporal-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_temporal_search.py "$(SYNTH_DIR)"
compositional-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_compositional_search.py "$(SYNTH_DIR)"
check-axi-dma-rtl:
	bash scripts/check_axi_dma_rtl.sh
run-axi-dma-rd-smoke:
	bash scripts/run_axi_dma_rd_smoke.sh
run-axi-dma-wr-smoke:
	bash scripts/run_axi_dma_wr_smoke.sh
run-axi-dma-workload:
	PYTHONPATH=src $(PYTHON) scripts/run_axi_dma_workload.py experiments/workloads/axi_dma_smoke.json out/axi-dma-workload
container-smoke:
	docker run --rm agcws:dev bash scripts/container_smoke.sh
