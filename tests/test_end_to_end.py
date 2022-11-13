import os
from pathlib import Path
from subprocess import Popen, PIPE
from typing import List

import pytest

TEST_CASES = [
    ("test_strip_init_cells.ipynb", "test_strip_init_cells.ipynb.expected", ["--strip-init-cells"]),
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells_dontdrop.ipynb.expected", []),
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells.ipynb.expected", ["--drop-empty-cells"]),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells_dontdrop.ipynb.expected", []),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells.ipynb.expected", ['--drop-tagged-cells=test']),
]

NOTEBOOKS_FOLDER = Path("tests/e2e_notebooks")


def get_nbstripout_exe():
    if 'NBSTRIPOUT_EXE' in os.environ:
        return os.environ['NBSTRIPOUT_EXE']
    return 'nbstripout'


@pytest.mark.parametrize("input_file, expected_file, args", TEST_CASES)
def test_end_to_end_nbstripout(input_file: str, expected_file: str, args: List[str]):
    with open(NOTEBOOKS_FOLDER / input_file, mode="r") as f:
        input = f.read().encode()

    with open(NOTEBOOKS_FOLDER / expected_file, mode="r") as f:
        expected = f.read().encode()

    pc = Popen([get_nbstripout_exe()] + args, stdin=PIPE, stdout=PIPE)
    output = pc.communicate(input=input)[0]

    assert output == expected
