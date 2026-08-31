from pathlib import Path

from agcws.policies.agent import OfflineAgent
from agcws.policies.prompt import load_frozen_prompt, prompt_hash


def test_frozen_prompt_has_stable_hash():
    path = Path("prompts/agent_system_v1.txt")
    content, digest = load_frozen_prompt(path)
    assert content
    assert digest == prompt_hash(path)


def test_offline_agent_records_frozen_prompt_hash():
    assert OfflineAgent(1).prompt_hash == prompt_hash(Path("prompts/agent_system_v1.txt"))
