from nbstripout._utils import pop_recursive


def test_pop_recursive():
    d = {'a': {'b': 1, 'c': 2}}
    assert pop_recursive(d, 'a.c') == 2
    assert d == {'a': {'b': 1}}
