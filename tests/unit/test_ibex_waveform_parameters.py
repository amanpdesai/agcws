from io import StringIO

import pytest

from agcws.designs.ibex.parameters import waveform_parameters


def test_configuration_comparison_requires_every_mapped_parameter():
    from agcws.designs.ibex.parameters import verify_parameters
    expected = {'MHPMCounterNum': 12, 'RV32M': 'ibex_pkg::RV32MFast',
                'DmHaltAddr': "32'h00100000"}
    observed = {'MHPMCounterNum': 12, 'RV32M': 2, 'DmHaltAddr': 1048576}
    assert verify_parameters(observed, expected) == observed
    for mismatch in ({**observed, 'MHPMCounterNum': 0}, {'MHPMCounterNum': 12}):
        with pytest.raises(ValueError, match='configuration differs'):
            verify_parameters(mismatch, expected)


def test_shared_identifier_keeps_every_parameter_name():
    source = '''$scope module core $end
$var parameter 1 ! FlagA $end
$var parameter 1 ! FlagB $end
$var parameter 32 " MHPMCounterNum [31:0] $end
$upscope $end
$enddefinitions $end
#0
0!
b1100 "
#1
1!
'''
    assert waveform_parameters(StringIO(source), 'core') == {
        'FlagA': 0, 'FlagB': 0, 'MHPMCounterNum': 12}


@pytest.mark.parametrize('value', ['', 'x!', 'z!'])
def test_missing_or_unknown_parameter_fails(value):
    with pytest.raises(ValueError):
        waveform_parameters(StringIO('$scope module core $end\n$var parameter 1 ! Flag $end\n'
                                     '$enddefinitions $end\n#0\n' + value + '\n#1\n'), 'core')
