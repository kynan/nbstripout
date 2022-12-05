from pathlib import Path
import sys

import pytest

# fix this before pytester.chdir() happens
NOTEBOOKS_FOLDER = Path("tests").absolute()


def test_diff_with_process_substitution(pytester: pytest.Pytester):
    if sys.platform.startswith("win"):
        pytest.skip("test requires proper bash shell", allow_module_level=True)

    r = pytester.run(
        'bash', 
        '-c', 
        f'"diff <( $nbstripout -t ${NOTEBOOKS_FOLDER / "test_diff.ipynb"} ) <( $nbstripout -t ${NOTEBOOKS_FOLDER / "test_diff_output.ipynb"} )"'
    )
    assert len(r.stdout.lines) == 0

    r = pytester.run(
        'bash', 
        '-c', 
        f'"diff <( $nbstripout -t ${NOTEBOOKS_FOLDER / "test_diff.ipynb"} ) <( $nbstripout -t ${NOTEBOOKS_FOLDER / "test_diff_different.ipynb"} )"'
    )
    assert len(r.stdout.lines) == 0