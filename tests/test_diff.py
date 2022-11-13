import os
from pathlib import Path
from subprocess import run, PIPE

NOTEBOOKS_FOLDER = Path("tests/diff_notebooks")


def get_bash_exe():
    if 'BASH_EXE' in os.environ:
        return os.environ['BASH_EXE']
    return 'bash'


def get_nbstripout_exe():
    if 'NBSTRIPOUT_EXE' in os.environ:
        return os.environ['NBSTRIPOUT_EXE']
    return 'nbstripout'


def test_diff_no_difference():
    expected = ""

    pc = run([get_bash_exe(), "-c", f"diff <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff.ipynb\" ) <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff_output.ipynb\" )"], stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert output == expected


def test_diff_diff():
    expected = """9c9
<     "print(\\"aou\\")"
---
>     "print(\\"aou now it is different\\")"
"""

    pc = run([get_bash_exe(), "-c", f"diff <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff.ipynb\" ) <( {get_nbstripout_exe()} -t \"{NOTEBOOKS_FOLDER}/test_diff_different.ipynb\" )"], stdout=PIPE, universal_newlines=True)
    output = pc.stdout

    assert output == expected
