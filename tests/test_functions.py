import nbstripout


def test_pos_recursive():
    d = {'a': {'b': 1, 'c': 2}}
    assert nbstripout.pop_recursive(d, 'a.c') == 2
    assert d  == {'a': {'b': 1}}
