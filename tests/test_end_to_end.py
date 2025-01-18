import os
from pathlib import Path
import re
from subprocess import run, PIPE

# Note: typing.Pattern is deprecated, for removal in 3.13 in favour of re.Pattern introduced in 3.8
from typing import List, Union, Pattern

import pytest

NOTEBOOKS_FOLDER = Path('tests/e2e_notebooks')

TEST_CASES = [
    ('test_drop_empty_cells.ipynb', 'test_drop_empty_cells_dontdrop.ipynb.expected', []),
    ('test_drop_empty_cells.ipynb', 'test_drop_empty_cells.ipynb.expected', ['--drop-empty-cells']),
    ('test_drop_tagged_cells.ipynb', 'test_drop_tagged_cells_dontdrop.ipynb.expected', []),
    ('test_drop_tagged_cells.ipynb', 'test_drop_tagged_cells.ipynb.expected', ['--drop-tagged-cells=test']),
    ('test_execution_timing.ipynb', 'test_execution_timing.ipynb.expected', []),
    ('test_max_size.ipynb', 'test_max_size.ipynb.expected', ['--max-size', '50', '--keep-id']),
    ('test_max_size.ipynb', 'test_max_size.ipynb.expected_sequential_id', ['--max-size', '50']),
    ('test_empty_metadata.ipynb', 'test_empty_metadata.ipynb.expected', []),
    ('test_metadata.ipynb', 'test_metadata.ipynb.expected', []),
    (
        'test_metadata.ipynb',
        'test_metadata_extra_keys.ipynb.expected',
        ['--extra-keys', 'metadata.kernelspec metadata.language_info'],
    ),
    ('test_metadata.ipynb', 'test_metadata_keep_count.ipynb.expected', ['--keep-count']),
    ('test_metadata.ipynb', 'test_metadata_keep_output.ipynb.expected', ['--keep-output']),
    ('test_metadata.ipynb', 'test_metadata_keep_output_keep_count.ipynb.expected', ['--keep-output', '--keep-count']),
    ('test_metadata_notebook.ipynb', 'test_metadata_notebook.ipynb.expected', []),
    (
        'test_keep_metadata_keys.ipynb',
        'test_keep_metadata_keys.ipynb.expected',
        ['--keep-metadata-keys', 'cell.metadata.scrolled cell.metadata.collapsed metadata.a'],
    ),
    (
        'test_metadata_period.ipynb',
        'test_metadata_period.ipynb.expected',
        [
            '--extra-keys',
            'cell.metadata.application/vnd.databricks.v1+cell metadata.application/vnd.databricks.v1+notebook',
        ],
    ),
    ('test_strip_init_cells.ipynb', 'test_strip_init_cells.ipynb.expected', ['--strip-init-cells']),
    ('test_nbformat2.ipynb', 'test_nbformat2.ipynb.expected', []),
    ('test_nbformat45.ipynb', 'test_nbformat45.ipynb.expected', ['--keep-id']),
    ('test_nbformat45.ipynb', 'test_nbformat45.ipynb.expected_sequential_id', []),
    ('test_missing_nbformat.ipynb', 'test_missing_nbformat.ipynb.expected', []),
    ('test_unicode.ipynb', 'test_unicode.ipynb.expected', []),
    ('test_widgets.ipynb', 'test_widgets.ipynb.expected', []),
    ('test_zeppelin.zpln', 'test_zeppelin.zpln.expected', ['--mode', 'zeppelin']),
]

DRY_RUN_CASES = [
    ('test_metadata.ipynb', [], True),
    ('test_zeppelin.zpln', ['--mode', 'zeppelin'], True),
    ('test_nochange.ipynb', [], False),
]

ERR_OUTPUT_CASES = [
    (
        'test_metadata.ipynb',
        ['Ignoring invalid extra key `invalid`', 'Ignoring invalid extra key `foo.invalid`'],
        ['--extra-keys', 'invalid foo.invalid'],
    ),
    (
        'test_metadata_exception.ipynb',
        [
            re.compile(
                '.*MetadataError: cell metadata contradicts tags: `keep_output` is false, but `keep_output` in tags'
            )
        ],
        [],
    ),
    ('test_invalid_json.ipynb', ['No valid notebook detected on stdin'], []),
]


def nbstripout_exe():
    return os.environ.get('NBSTRIPOUT_EXE', 'nbstripout')


@pytest.mark.parametrize('input_file, expected_file, args', TEST_CASES)
@pytest.mark.parametrize('verify', (True, False))
def test_end_to_end_stdin(input_file: str, expected_file: str, args: List[str], verify: bool):
    with open(NOTEBOOKS_FOLDER / expected_file, mode='r') as f:
        expected = f.read()

    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        input_ = f.read()

    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        args = [nbstripout_exe()] + args
        if verify:
            args.append('--verify')
        pc = run(args, stdin=f, stdout=PIPE, universal_newlines=True)
        output = pc.stdout

    if verify:
        # When using stin, the dry run flag is disregarded.
        assert pc.returncode == (1 if input_ != expected else 0)
    else:
        assert output == expected
        assert pc.returncode == 0


@pytest.mark.parametrize('input_file, expected_file, args', TEST_CASES)
@pytest.mark.parametrize('verify', (True, False))
def test_end_to_end_file(input_file: str, expected_file: str, args: List[str], tmp_path, verify: bool):
    with open(NOTEBOOKS_FOLDER / expected_file, mode='r') as f:
        expected = f.read()

    p = tmp_path / input_file
    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        p.write_text(f.read())

    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        input_ = f.read()

    args = [nbstripout_exe(), p] + args
    if verify:
        args.append('--verify')
    pc = run(args, stdout=PIPE, universal_newlines=True)

    output = pc.stdout.strip()
    if verify:
        if expected != input_:
            assert 'Dry run: would have stripped' in output
            assert pc.returncode == 1

        # Since verify implies --dry-run, we make sure the file is not modified
        with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
            output_ = f.read()

        assert output_ == input_
    else:
        assert pc.returncode == 0
        assert not pc.stdout and p.read_text() == expected


@pytest.mark.parametrize('input_file, extra_args, any_change', DRY_RUN_CASES)
@pytest.mark.parametrize('verify', (True, False))
def test_dry_run_stdin(input_file: str, extra_args: List[str], any_change: bool, verify: bool):
    expected = 'Dry run: would have stripped input from stdin\n'

    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        args = [nbstripout_exe(), '--dry-run'] + extra_args
        if verify:
            args.append('--verify')
        pc = run(args, stdin=f, stdout=PIPE, universal_newlines=True)
        output = pc.stdout

    assert output == (expected if any_change else '')
    assert pc.returncode == (1 if verify and any_change else 0)


@pytest.mark.parametrize('input_file, extra_args, any_change', DRY_RUN_CASES)
@pytest.mark.parametrize('verify', (True, False))
def test_dry_run_args(input_file: str, extra_args: List[str], any_change: bool, verify: bool):
    expected_regex = re.compile(f'Dry run: would have stripped .*[/\\\\]{input_file}\n')
    args = [
        nbstripout_exe(),
        str(NOTEBOOKS_FOLDER / input_file),
        '--dry-run',
    ] + extra_args
    if verify:
        args.append('--verify')
    pc = run(args, stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert expected_regex.match(output) if any_change else output == ''
    assert pc.returncode == (1 if verify and any_change else 0)


@pytest.mark.parametrize('input_file, expected_errs, extra_args', ERR_OUTPUT_CASES)
def test_make_errors(input_file: str, expected_errs: List[Union[str, Pattern]], extra_args: List[str]):
    with open(NOTEBOOKS_FOLDER / input_file, mode='r') as f:
        pc = run([nbstripout_exe(), '--dry-run'] + extra_args, stdin=f, stderr=PIPE, universal_newlines=True)
        err_output = pc.stderr

    for e in expected_errs:
        if isinstance(e, Pattern):
            assert e.search(err_output)
        else:
            assert e in err_output
