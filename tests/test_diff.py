import os
from pathlib import Path
from subprocess import run, PIPE
import sys

import pytest

NOTEBOOKS_FOLDER = Path("tests/diff_notebooks")


def get_nbstripout_exe():
    if 'NBSTRIPOUT_EXE' in os.environ:
        return os.environ['NBSTRIPOUT_EXE']
    return 'nbstripout'


def test_diff_no_difference():
    if sys.platform == 'win32' and 'bash' not in os.environ['COMSPEC']:
        pytest.skip(f"This test requires the bash shell on windows, not {os.environ['COMSPEC']}")

    expected = ""

    pc = run(f"diff <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff.ipynb\" ) <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff_output.ipynb\" )", shell=True, stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert output == expected


def test_diff_diff():
    if sys.platform == 'win32' and 'bash' not in os.environ['COMSPEC']:
        pytest.skip(f"This test requires the bash shell on windows, not {os.environ['COMSPEC']}")

    expected = """9c9
<     "print(\\"aou\\")"
---
>     "print(\\"aou now it is different\\")"
"""

    pc = run(f"diff <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff.ipynb\" ) <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff_different.ipynb\" )", shell=True, stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert output == expected
