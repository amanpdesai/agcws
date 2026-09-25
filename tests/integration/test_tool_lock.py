import re
import subprocess
from pathlib import Path


def lock_value(name):
    assert re.fullmatch(r'[A-Z_][A-Z_0-9]*', name)
    return subprocess.check_output(
        ['sh', '-c', f'. ./tools/tools.lock; printf "%s" "${name}"'], text=True
    )


def test_base_and_source_pins_match_existing_contracts():
    from agcws.evaluation.power.verify_windows import PIN

    assert f'FROM {lock_value("BASE_IMAGE")}' in Path('docker/Dockerfile').read_text()
    assert lock_value('OPENSTA_REF') == PIN
    for name in ('OPENSTA', 'CHIA', 'SV_ELAB', 'BOOST_REGEX', 'VERILATOR', 'YOSYS',
                 'IVERILOG', 'CUDD'):
        pin = lock_value(name + '_REF')
        assert re.fullmatch(r'[0-9a-f]{40}', pin)
        path = 'tools/' + name.lower().replace('_', '-')
        entry = subprocess.check_output(['git', 'ls-files', '--stage', path], text=True)
        assert entry.split()[0] == '160000'
        assert entry.split()[1] == pin


def test_sources_come_from_exported_submodules_not_network_clones():
    text = Path('docker/Dockerfile').read_text()
    for name in ('yosys', 'iverilog', 'cudd', 'opensta', 'sv-elab', 'boost-regex', 'chia'):
        assert f'COPY --from=tool_sources {name} ' in text
    assert 'git clone' not in text
    assert 'COPY --from=tool_sources verilator ' in Path('docker/benchmark.Dockerfile').read_text()


def test_both_builds_consume_tool_lock():
    main = Path('docker/Dockerfile').read_text()
    benchmark = Path('docker/benchmark.Dockerfile').read_text()
    for text in (main, benchmark):
        assert 'COPY tools/tools.lock /opt/agcws/tools.lock' in text
        assert '. /opt/agcws/tools.lock' in text
    for name in ('VERILATOR_PACKAGE', 'RISCV_GCC_PACKAGE', 'RISCV_BINUTILS_PACKAGE',
                 'GTKWAVE_PACKAGE', 'GPERF_PACKAGE'):
        assert re.fullmatch(r'[a-z0-9+-]+=[^\s=]+', lock_value(name))
        assert f'"${name}"' in main
    for name in ('AUTOCONF_PACKAGE', 'HELP2MAN_PACKAGE', 'PICOLIBC_PACKAGE'):
        assert f'"${name}"' in benchmark
    assert 'ARG BASE_IMAGE=agcws:dev' not in benchmark
    assert 'COPY tools/chia' not in main


def test_export_preserves_pinned_nested_sources_and_ignores_worktree_edits(tmp_path):
    destination = tmp_path / 'sources'
    before = subprocess.check_output(['git', '-C', 'tools/chia', 'status', '--porcelain'])
    subprocess.run(['bash', 'docker/export-tools.sh', str(destination)], check=True)
    assert (destination / 'yosys/abc/Makefile').is_file()
    assert (destination / 'sv-elab/third_party/slang/CMakeLists.txt').is_file()
    assert '$Format' not in (destination / 'yosys/.gitcommit').read_text()
    assert '$Format' not in (destination / 'yosys/abc/.gitcommit').read_text()
    assert not (destination / 'chia/.git').exists()
    expected = subprocess.check_output(['git', '-C', 'tools/chia', 'show',
                                        lock_value('CHIA_REF') + ':pyproject.toml'])
    assert (destination / 'chia/pyproject.toml').read_bytes() == expected
    assert subprocess.check_output(['git', '-C', 'tools/chia', 'status', '--porcelain']) == before
    assert subprocess.run(['bash', 'docker/export-tools.sh', str(destination)]).returncode != 0


def test_direct_build_dependencies_and_hardware_python_tools_are_pinned():
    for package in lock_value('BUILD_PACKAGES').split():
        assert re.fullmatch(r'[a-z0-9+-]+=[^\s=]+', package)
    text = Path('docker/Dockerfile').read_text()
    for name in ('PIP_VERSION', 'SETUPTOOLS_VERSION', 'WHEEL_VERSION', 'FUSESOC_VERSION',
                 'EDALIZE_VERSION', 'COCOTB_VERSION', 'COCOTB_TEST_VERSION',
                 'COCOTBEXT_AXI_VERSION', 'MYHDL_VERSION'):
        assert re.fullmatch(r'[0-9]+(?:\.[0-9]+)+', lock_value(name))
        assert f'==${name}' in text
