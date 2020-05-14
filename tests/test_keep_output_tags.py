from copy import deepcopy
import os
import re

import nbformat
import pytest

from nbstripout import strip_output, MetadataError

directory = os.path.dirname(__file__)


@pytest.fixture
def orig_nb():
    fname = 'test_keep_output_tags.ipynb'
    return nbformat.read(os.path.join(directory, fname), nbformat.NO_CONVERT)


@pytest.fixture
def nb_with_exception():
    fname = 'test_keep_output_tags_exception.ipynb'
    return nbformat.read(os.path.join(directory, fname), nbformat.NO_CONVERT)


def test_cells(orig_nb):
    nb_stripped = deepcopy(orig_nb)
    nb_stripped = strip_output(nb_stripped, None, None)
    for i, cell in enumerate(nb_stripped.cells):
        if cell.cell_type == 'code' and cell.source:
            match = re.match(r"\s*#\s*(output|no_output)", cell.source)
            if match:
                # original cell should have had output.
                # If not, there's a problem with the test fixture
                assert orig_nb.cells[i].outputs

                if match.group(1) == 'output':
                    assert len(cell.outputs) > 0
                else:
                    assert len(cell.outputs) == 0


def test_exception(nb_with_exception):
    with pytest.raises(MetadataError):
        strip_output(nb_with_exception, None, None)
