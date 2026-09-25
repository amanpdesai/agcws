"""The public CLI must dispatch without accidentally running experiments."""

import pytest

from agcws.cli import COMMANDS, main


@pytest.mark.parametrize("group,action", [
    (group, action) for group, actions in COMMANDS.items()
    for action in actions
])
def test_command_help_does_not_execute(group, action, capsys):
    with pytest.raises(SystemExit) as exc:
        main([group, action, "--help"])
    assert exc.value.code == 0
    assert "usage:" in capsys.readouterr().out


def test_doctor_returns_success_not_a_dict(monkeypatch, capsys):
    from agcws.cli import doctor

    monkeypatch.setattr(doctor, "main", lambda argv: {"checked": True})
    assert main(["doctor"]) is None
