import pytest

from agcws.designs.aes.gls import validate_interface


def interface():
    return {'modules': {'aes_cipher_core': {'ports': {
        'state_init_i': {'direction': 'input', 'bits': list(range(128))},
        'state_o': {'direction': 'output', 'bits': list(range(128))},
    }}}}


def test_mapped_interface_uses_structural_ports():
    validate_interface(interface())


@pytest.mark.parametrize('change', ['width', 'direction', 'missing', 'wrong_top'])
def test_mapped_interface_rejects_wrong_ports(change):
    netlist = interface()
    ports = netlist['modules']['aes_cipher_core']['ports']
    if change == 'width':
        ports['state_init_i']['bits'].pop()
    elif change == 'direction':
        ports['state_o']['direction'] = 'input'
    elif change == 'missing':
        del ports['state_o']
    else:
        netlist['modules']['other'] = netlist['modules'].pop('aes_cipher_core')
    with pytest.raises(ValueError, match='unmasked state interface'):
        validate_interface(netlist)
