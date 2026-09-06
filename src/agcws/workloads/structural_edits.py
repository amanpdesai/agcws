"""Budget-preserving schedule edits shared by classical and agent policies."""
from agcws.workloads.schedule import expand_schedule


def apply_structural_edit(schedule, contract, edit):
    sequence = expand_schedule(schedule, contract)
    operation = edit['op']
    fields = {'swap': {'op', 'a', 'b'}, 'move': {'op', 'a', 'b'},
              'split': {'op', 'a', 'amount'}, 'merge': {'op', 'a', 'b'},
              'redistribute': {'op', 'a', 'b', 'amount'}}
    if operation not in fields or set(edit) != fields[operation]:
        raise ValueError('unknown edit operation or fields')
    for key in ('a', 'b'):
        if key in edit and (type(edit[key]) is not int or not 0 <= edit[key] < len(sequence)):
            raise ValueError('edit index out of range')
    a = edit['a']
    field = 'units' if sequence[a]['op'] == 'work' else 'cycles'
    if operation in ('split', 'redistribute') and (type(edit['amount']) is not int or edit['amount'] <= 0):
        raise ValueError('edit amount must be a positive integer')
    if operation == 'split':
        if not edit['amount'] < sequence[a][field]:
            raise ValueError('split must leave two positive parts')
        sequence[a][field] -= edit['amount']
        sequence.insert(a + 1, {'op': sequence[a]['op'], field: edit['amount']})
    else:
        b = edit['b']
        if a == b:
            raise ValueError('edit indices must differ')
        if operation == 'swap':
            sequence[a], sequence[b] = sequence[b], sequence[a]
        elif operation == 'move':
            sequence.insert(b, sequence.pop(a))
        else:
            if sequence[a]['op'] != sequence[b]['op']:
                raise ValueError('merge/redistribute requires matching operation types')
            if operation == 'merge':
                sequence[a][field] += sequence[b][field]
                sequence.pop(b)
            else:
                if edit['amount'] >= sequence[a][field]:
                    raise ValueError('redistribution must leave positive work or idle')
                sequence[a][field] -= edit['amount']
                sequence[b][field] += edit['amount']
    candidate = {'sequence': sequence}
    expand_schedule(candidate, contract)
    return candidate


def random_structural_edit(schedule, contract, rng):
    """Sample a legal edit directly; do not retry invalid proposals."""
    sequence = expand_schedule(schedule, contract)
    pairs = [(a, b) for a in range(len(sequence)) for b in range(len(sequence)) if a != b]
    same = [(a, b) for a, b in pairs if sequence[a]['op'] == sequence[b]['op']]
    splittable = [i for i, node in enumerate(sequence) if node.get('units', node.get('cycles')) > 1]
    actions = []
    if pairs:
        actions.extend(['swap', 'move'])
    if same:
        actions.append('merge')
    if splittable and len(sequence) < contract.max_expanded_ops:
        actions.append('split')
    donors = [(a, b) for a, b in same if a in splittable]
    if donors:
        actions.append('redistribute')
    if not actions:
        return {'sequence': sequence}
    operation = rng.choice(actions)
    if operation == 'split':
        a = rng.choice(splittable)
        count = sequence[a].get('units', sequence[a].get('cycles'))
        edit = {'op': operation, 'a': a, 'amount': rng.randrange(1, count)}
    else:
        a, b = rng.choice(donors if operation == 'redistribute' else same if operation == 'merge' else pairs)
        edit = {'op': operation, 'a': a, 'b': b}
        if operation == 'redistribute':
            count = sequence[a].get('units', sequence[a].get('cycles'))
            edit['amount'] = rng.randrange(1, count)
    return apply_structural_edit(schedule, contract, edit)
