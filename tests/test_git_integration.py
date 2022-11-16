from configparser import ConfigParser
from pathlib import Path
import re

import pytest

# fix this before pytester.chdir() happens
NOTEBOOKS_FOLDER = Path("tests").absolute()


def test_install(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    assert pytester.run('nbstripout', '--is-installed').ret == 1
    pytester.run('nbstripout', '--install')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    with open(".git/info/attributes", "r") as f:
        attr_lines = f.readlines()
    assert "*.ipynb filter=nbstripout\n" in attr_lines
    assert "*.zpln filter=nbstripout\n" in attr_lines
    assert "*.ipynb diff=ipynb\n" in attr_lines

    config = ConfigParser()
    config.read(".git/config")
    assert re.match(r".*python.* -m nbstripout", config['filter "nbstripout"']["clean"])
    assert config['filter "nbstripout"']["smudge"] == "cat"
    assert re.match(r".*python.* -m nbstripout -t", config['diff "ipynb"']["textconv"])


def test_uninstall(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    # add extra filter at the start, so we can check we don't remove it
    pytester.path.joinpath(".git/info/attributes").write_text("*.txt text")

    # do the install and verify
    pytester.run('nbstripout', '--install')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    # uninstall and verify (the actual test)
    pytester.run('nbstripout', '--uninstall')
    assert pytester.run('nbstripout', '--is-installed').ret == 1

    with open(".git/info/attributes", "r") as f:
        attr_lines = f.readlines()
    assert "*.txt text\n" in attr_lines  # still there and not removed
    assert len(attr_lines) == 1

    config = ConfigParser()
    config.read(".git/config")
    assert 'filter "nbstripout"' not in config
    assert 'diff "ipynb"'not in config


def test_git_diff_nodiff(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run('git', 'config', '--local', 'filter.nbstripout.extrakeys', ' ')
    pytester.run('nbstripout', '--install')

    r = pytester.run('git', 'diff', '--no-index', '--no-ext-diff', '--unified=0', '--exit-code', '-a', '--no-prefix',
                     NOTEBOOKS_FOLDER / "test_diff.ipynb", NOTEBOOKS_FOLDER / "test_diff_output.ipynb")
    assert r.ret == 0
    assert not r.outlines


def test_git_diff_diff(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run('git', 'config', '--local', 'filter.nbstripout.extrakeys', ' ')
    pytester.run('nbstripout', '--install')

    r = pytester.run('git', 'diff', '--no-index', NOTEBOOKS_FOLDER / "test_diff.ipynb", NOTEBOOKS_FOLDER / "test_diff_different_extrakeys.ipynb")
    assert r.ret == 1
    r.stdout.fnmatch_lines([
        r'index*',
        r'--- *test_diff.ipynb*',
        r'+++ *test_diff_different_extrakeys.ipynb*',
        r'@@ -6,15 +6,14 @@',
        r'    "metadata": {},',
        r'    "outputs": [],',
        r'    "source": [',
        r'-    "print(\"aou\")"',
        r'+    "print(\"aou now it is different\")"',
        r'    ]',
        r'   }',
        r'  ],',
        r'  "metadata": {',
        r'   "kernelspec": {',
        r'    "display_name": "Python 2",',
        r'-   "language": "python",',
        r'-   "name": "python2"',
        r'+   "language": "python"',
        r'   },',
        r'   "language_info": {',
        r'    "codemirror_mode": {',
    ])
    assert len(r.outlines) == 22  # 21 lines + new line at end


def test_git_diff_extrakeys(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run('git', 'config', '--local', 'filter.nbstripout.extrakeys', 'cell.metadata.collapsed metadata.kernelspec.name')
    pytester.run('nbstripout', '--install')

    r = pytester.run('git', 'diff', '--no-index', NOTEBOOKS_FOLDER / "test_diff.ipynb", NOTEBOOKS_FOLDER / "test_diff_different_extrakeys.ipynb")
    assert r.ret == 1
    r.stdout.fnmatch_lines([
        r'index*',
        r'--- *test_diff.ipynb*',
        r'+++ *test_diff_different_extrakeys.ipynb*',
        r'@@ -6,7 +6,7 @@',
        r'    "metadata": {},',
        r'    "outputs": [],',
        r'    "source": [',
        r'-    "print(\"aou\")"',
        r'+    "print(\"aou now it is different\")"',
        r'    ]',
        r'   }',
        r'  ],',
    ])
    assert len(r.outlines) == 13  # 12 lines + new line at end
