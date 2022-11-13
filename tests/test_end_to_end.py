import os
from pathlib import Path
import re
from subprocess import run
from typing import List

import pytest

NOTEBOOKS_FOLDER = Path("tests/e2e_notebooks")

TEST_CASES = [
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells_dontdrop.ipynb.expected", []),
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells.ipynb.expected", ["--drop-empty-cells"]),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells_dontdrop.ipynb.expected", []),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells.ipynb.expected", ['--drop-tagged-cells=test']),
    ("test_execution_timing.ipynb", "test_execution_timing.ipynb.expected", []),
    ("test_strip_init_cells.ipynb", "test_strip_init_cells.ipynb.expected", ["--strip-init-cells"]),
    ("test_unicode.ipynb", "test_unicode.ipynb.expected", []),
    ("test_widgets.ipynb", "test_widgets.ipynb.expected", []),
    ("test_zeppelin.zpln", "test_zeppelin.zpln.expected", ["--mode", "zeppelin"]),
]

DRY_RUN_CASES = [
    ("test_metadata.ipynb", []),
    ("test_zeppelin.zpln", ["--mode", "zeppelin"]),
]


def get_nbstripout_exe():
    if 'NBSTRIPOUT_EXE' in os.environ:
        return os.environ['NBSTRIPOUT_EXE']
    return 'nbstripout'


@pytest.mark.parametrize("input_file, expected_file, args", TEST_CASES)
def test_end_to_end_nbstripout(input_file: str, expected_file: str, args: List[str]):
    with open(NOTEBOOKS_FOLDER / expected_file, mode="r") as f:
        expected = f.read()

    with open(NOTEBOOKS_FOLDER / input_file, mode="r") as f:
        pc = run([get_nbstripout_exe()] + args, stdin=f, capture_output=True, text=True)
        output = pc.stdout

    assert output == expected


@pytest.mark.parametrize("input_file, extra_args", DRY_RUN_CASES)
def test_dry_run_stdin(input_file: str, extra_args: List[str]):
    expected = "Dry run: would have stripped input from stdin\n"

    with open(NOTEBOOKS_FOLDER / input_file, mode="r") as f:
        pc = run([get_nbstripout_exe(), "--dry-run"] + extra_args, stdin=f, capture_output=True, text=True)
        output = pc.stdout

    assert output == expected


@pytest.mark.parametrize("input_file, extra_args", DRY_RUN_CASES)
def test_dry_run_args(input_file: str, extra_args: List[str]):
    expected_regex = re.compile(f"Dry run: would have stripped .*[/\\\\]{input_file}\n")

    pc = run([get_nbstripout_exe(), NOTEBOOKS_FOLDER / input_file, "--dry-run", ] + extra_args, capture_output=True, text=True)
    output = pc.stdout

    assert expected_regex.match(output)
