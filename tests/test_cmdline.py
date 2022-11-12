from pathlib import Path
from subprocess import Popen, PIPE
from typing import List


def run_nbstripout_compare_output(input_file: Path, expected_file: Path, args: List[str] = []):
    with open(input_file, mode="r") as f:
        input = f.read().encode()

    with open(expected_file, mode="r") as f:
        expected = f.read().encode()

    pc = Popen(["nbstripout"] + args, stdin=PIPE, stdout=PIPE)
    output = pc.communicate(input=input)[0]

    assert output == expected


def test_strip_init_cells():
    run_nbstripout_compare_output(Path("tests/test_strip_init_cells.ipynb"), Path("tests/test-strip-init-cells.t"), ["--strip-init-cells"])


def test_drop_empty_cells_dont_drop():
    run_nbstripout_compare_output(Path("tests/test_drop_empty_cells.ipynb"), Path("tests/test_drop_empty_cells_dontdrop.ipynb.expected"))


def test_drop_empty_cells():
    run_nbstripout_compare_output(Path("tests/test_drop_empty_cells.ipynb"), Path("tests/test_drop_empty_cells.ipynb.expected"), ["--drop-empty-cells"])
