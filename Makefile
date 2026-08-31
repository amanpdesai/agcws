.DEFAULT_GOAL := test
PYTHON ?= python3
SYNTH_DIR ?= out/aes-core-synthesis
WORKLOAD ?= experiments/workloads/aes_min_scored.json
EVAL_DIR ?= out/aes-evaluation

.PHONY: test lint inspect-liberty synth-aes evaluate-aes temporal-search container-smoke
test:
	$(PYTHON) -m pytest -q
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
temporal-search:
	PYTHONPATH=src $(PYTHON) scripts/run_aes_temporal_search.py "$(SYNTH_DIR)"
container-smoke:
	docker run --rm agcws:dev bash scripts/container_smoke.sh
