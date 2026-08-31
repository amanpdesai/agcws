from agcws.policies.mutation import MutationSearch


def test_mutation_preserves_aes_configuration_and_is_reproducible():
    workload = {"data_pattern": 0, "operations": [
        {"op": "configure", "key_len": 128},
        {"op": "encrypt", "blocks": 24},
    ]}
    first = MutationSearch(5)._mutate(workload)
    second = MutationSearch(5)._mutate(workload)
    assert first == second
    assert first["operations"][0]["op"] == "configure"
