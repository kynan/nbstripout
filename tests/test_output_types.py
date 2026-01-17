import os
from copy import deepcopy

import nbformat
import pytest

from nbstripout import strip_output

directory = os.path.dirname(__file__)


@pytest.fixture
def orig_nb():
    # Grab the original notebook
    fname = 'test_output_types.ipynb'
    return nbformat.read(os.path.join(directory, fname), nbformat.NO_CONVERT)


def test_drop_errors(orig_nb):
    """
    Confirm that --drop-output-types works as expected,
    when asking just to drop `error` outputs.
    """
    nb_stripped = strip_output(
        deepcopy(orig_nb), keep_output=True, keep_count=False, keep_id=False, drop_output_types={'error'}
    )

    # No outputs in the markdown
    assert not hasattr(nb_stripped.cells[0], 'outputs')

    # Original cell should have 3 outputs, with the last being error
    assert len(orig_nb.cells[1].outputs) == 3
    assert orig_nb.cells[1].outputs[2]['output_type'] == 'error'

    # Second cell should have a stdout stream, stderr stream and an error
    stripped_output_1 = nb_stripped.cells[1].outputs[0]
    stripped_output_2 = nb_stripped.cells[1].outputs[1]
    assert len(nb_stripped.cells[1].outputs) == 2
    assert stripped_output_1['output_type'] == 'stream'
    assert stripped_output_2['output_type'] == 'stream'
    assert stripped_output_1['name'] == 'stdout'
    assert stripped_output_2['name'] == 'stderr'

    # Third cell should have an execution output
    assert len(nb_stripped.cells[2].outputs) == 1
    assert nb_stripped.cells[2].outputs[0]['output_type'] == 'execute_result'


def test_keep_output(orig_nb):
    """
    Confirm that --keep-output-types works as expected,
    dropping all but `execute_result` outputs from the notebook.
    """
    nb_stripped = strip_output(
        deepcopy(orig_nb), keep_output=True, keep_count=False, keep_id=False, keep_output_types={'execute_result'}
    )

    # No outputs in the markdown
    assert not hasattr(nb_stripped.cells[0], 'outputs')

    # Original cell should have 3 outputs, with the last being error
    assert len(orig_nb.cells[1].outputs) == 3
    assert orig_nb.cells[1].outputs[2]['output_type'] == 'error'

    # All outputs should be stripped in the second cell
    assert len(nb_stripped.cells[1].outputs) == 0

    # Third cell should have an execution output
    assert len(nb_stripped.cells[2].outputs) == 1


def test_output_format_tags(orig_nb):
    """
    Confirm that both <output_type>:<name> and <output_type> formats work.
    """
    nb_stripped = strip_output(
        deepcopy(orig_nb),
        keep_output=False,
        keep_count=False,
        keep_id=False,
        keep_output_types={'stream:stdout', 'execute_result'},
    )

    # No outputs in the markdown
    assert not hasattr(nb_stripped.cells[0], 'outputs')

    # Stripping all but stdout should leave only the print statement
    assert len(orig_nb.cells[1].outputs) == 3
    assert len(nb_stripped.cells[1].outputs) == 1

    # Third cell should have only the execute_result
    assert len(nb_stripped.cells[2].outputs) == 1
