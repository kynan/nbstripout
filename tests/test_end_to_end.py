import os
from pathlib import Path
import re
from subprocess import run, PIPE
# Note: typing.Pattern is deprecated, for removal in 3.13 in favour of re.Pattern introduced in 3.8
from typing import List, Union, Pattern

import pytest

NOTEBOOKS_FOLDER = Path("tests/e2e_notebooks")

TEST_CASES = [
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells_dontdrop.ipynb.expected", []),
    ("test_drop_empty_cells.ipynb", "test_drop_empty_cells.ipynb.expected", ["--drop-empty-cells"]),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells_dontdrop.ipynb.expected", []),
    ("test_drop_tagged_cells.ipynb", "test_drop_tagged_cells.ipynb.expected", ['--drop-tagged-cells=test']),
    ("test_execution_timing.ipynb", "test_execution_timing.ipynb.expected", []),
    ("test_max_size.ipynb", "test_max_size.ipynb.expected", ["--max-size", "50", "--keep-id"]),
    ("test_max_size.ipynb", "test_max_size.ipynb.expected_id", ["--max-size", "50"]),
    ("test_metadata.ipynb", "test_metadata.ipynb.expected", []),
    ("test_metadata.ipynb", "test_metadata_extra_keys.ipynb.expected", ["--extra-keys", "metadata.kernelspec metadata.language_info"]),
    ("test_metadata.ipynb", "test_metadata_keep_count.ipynb.expected", ["--keep-count"]),
    ("test_metadata.ipynb", "test_metadata_keep_output.ipynb.expected", ["--keep-output"]),
    ("test_metadata.ipynb", "test_metadata_keep_output_keep_count.ipynb.expected", ["--keep-output", "--keep-count"]),
    ("test_metadata_notebook.ipynb", "test_metadata_notebook.ipynb", []),
    ("test_keep_metadata_keys.ipynb", "test_keep_metadata_keys.ipynb.expected", ["--keep-metadata-keys", "cell.metadata.scrolled cell.metadata.collapsed metadata.a"]),
    ("test_metadata_period.ipynb", "test_metadata_period.ipynb.expected", ["--extra-keys", "cell.metadata.application/vnd.databricks.v1+cell metadata.application/vnd.databricks.v1+notebook"]),
    ("test_strip_init_cells.ipynb", "test_strip_init_cells.ipynb.expected", ["--strip-init-cells"]),
    ("test_nbformat2.ipynb", "test_nbformat2.ipynb.expected", []),
    ("test_nbformat45.ipynb", "test_nbformat45.ipynb.expected", ["--keep-id"]),
    ("test_nbformat45.ipynb", "test_nbformat45.ipynb.expected_id", []),
    ("test_unicode.ipynb", "test_unicode.ipynb.expected", []),
    ("test_widgets.ipynb", "test_widgets.ipynb.expected", []),
    ("test_zeppelin.zpln", "test_zeppelin.zpln.expected", ["--mode", "zeppelin"]),
]

DRY_RUN_CASES = [
    ("test_metadata.ipynb", []),
    ("test_zeppelin.zpln", ["--mode", "zeppelin"]),
]

ERR_OUTPUT_CASES = [
    ("test_metadata.ipynb", ["Ignoring invalid extra key `invalid`", "Ignoring invalid extra key `foo.invalid`"], ["--extra-keys", "invalid foo.invalid"]),
    ("test_metadata_exception.ipynb", [re.compile(".*MetadataError: cell metadata contradicts tags: `keep_output` is false, but `keep_output` in tags")], [])
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
        pc = run([get_nbstripout_exe()] + args, stdin=f, stdout=PIPE, universal_newlines=True)
        output = pc.stdout

    assert output == expected


@pytest.mark.parametrize("input_file, extra_args", DRY_RUN_CASES)
def test_dry_run_stdin(input_file: str, extra_args: List[str]):
    expected = "Dry run: would have stripped input from stdin\n"

    with open(NOTEBOOKS_FOLDER / input_file, mode="r") as f:
        pc = run([get_nbstripout_exe(), "--dry-run"] + extra_args, stdin=f, stdout=PIPE, universal_newlines=True)
        output = pc.stdout

    assert output == expected


@pytest.mark.parametrize("input_file, extra_args", DRY_RUN_CASES)
def test_dry_run_args(input_file: str, extra_args: List[str]):
    expected_regex = re.compile(f"Dry run: would have stripped .*[/\\\\]{input_file}\n")

    pc = run([get_nbstripout_exe(), str(NOTEBOOKS_FOLDER / input_file), "--dry-run", ] + extra_args, stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert expected_regex.match(output)


@pytest.mark.parametrize("input_file, expected_errs, extra_args", ERR_OUTPUT_CASES)
def test_make_errors(input_file: str, expected_errs: List[Union[str, Pattern]], extra_args: List[str]):
    with open(NOTEBOOKS_FOLDER / input_file, mode="r") as f:
        pc = run([get_nbstripout_exe(), "--dry-run"] + extra_args, stdin=f, stderr=PIPE, universal_newlines=True)
        err_output = pc.stderr

    for e in expected_errs:
        if isinstance(e, Pattern):
            assert e.search(err_output)
        else:
            assert e in err_output
