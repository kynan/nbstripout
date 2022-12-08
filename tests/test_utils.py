import pytest

from nbstripout._utils import pop_recursive


def make_dict():
    return {'a': {'b': 1, 'c': 2, 'd.e': 3, 'f': {'g': 4}}}


def make_data(default=None):
    return [
        ('a.c', 2, {'a': {'b': 1, 'd.e': 3, 'f': {'g': 4}}}),
        ('a.d.e', 3, {'a': {'b': 1, 'c': 2, 'f': {'g': 4}}}),
        ('a.f', {'g': 4}, {'a': {'b': 1, 'c': 2, 'd.e': 3}}),
        ('a.f.g', 4, {'a': {'b': 1, 'c': 2, 'd.e': 3, 'f': {}}}),
        ('a', {'b': 1, 'c': 2, 'd.e': 3, 'f': {'g': 4}}, {}),
        ('notfound', default, make_dict()),
        ('a.notfound', default, make_dict()),
        ('a.b.notfound', default, make_dict()),
    ]


@pytest.fixture
def d():
    return make_dict()


@pytest.mark.parametrize(('key', 'res', 'remainder'), make_data())
def test_pop_recursive(d, key, res, remainder):
    assert pop_recursive(d, key) == res
    assert d == remainder


@pytest.mark.parametrize(('key', 'res', 'remainder'), make_data(default=0))
def test_pop_recursive_default(d, key, res, remainder):
    assert pop_recursive(d, key, default=0) == res
    assert d == remainder
