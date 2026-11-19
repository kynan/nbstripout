import sys
from pathlib import Path

import pytest

# fix this before pytester.chdir() happens
NOTEBOOKS_FOLDER = Path('tests').absolute()

pytestmark = pytest.mark.skipif(sys.platform.startswith('win'), reason='test requires proper bash shell')


def test_diff_with_process_substitution_nodiff(pytester: pytest.Pytester):

    r = pytester.run(
        'bash',
        '-c',
        f'diff <( nbstripout -t {NOTEBOOKS_FOLDER / "test_diff.ipynb"} ) <( nbstripout -t {NOTEBOOKS_FOLDER / "test_diff_output.ipynb"} )',
    )
    assert not r.outlines
    assert r.ret == 0


def test_diff_with_process_substitution_diff(pytester: pytest.Pytester):

    r = pytester.run(
        'bash',
        '-c',
        f'diff <( nbstripout -t {NOTEBOOKS_FOLDER / "test_diff.ipynb"} ) <( nbstripout -t {NOTEBOOKS_FOLDER / "test_diff_different.ipynb"} )',
    )
    r.stdout.re_match_lines(
        r"""(.*)
<     "print(\"aou\")"
---
(.*\"print\(\\\"aou now it is different\\\"\)\")
""".splitlines()
    )
    assert r.ret == 1
