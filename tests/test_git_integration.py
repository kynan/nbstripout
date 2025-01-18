from configparser import ConfigParser
from pathlib import Path
import re
import sys

import pytest

# fix this before pytester.chdir() happens
NOTEBOOKS_FOLDER = Path('tests').absolute()


def test_install(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    assert pytester.run('nbstripout', '--is-installed').ret == 1
    pytester.run('nbstripout', '--install')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    with open('.git/info/attributes', 'r') as f:
        attr_lines = f.readlines()
    assert '*.ipynb filter=nbstripout\n' in attr_lines
    assert '*.zpln filter=nbstripout\n' in attr_lines
    assert '*.ipynb diff=ipynb\n' in attr_lines

    config = ConfigParser()
    config.read('.git/config')
    assert re.match(r'.*python.* -m nbstripout', config['filter "nbstripout"']['clean'])
    assert config['filter "nbstripout"']['required'] == 'true'
    assert config['filter "nbstripout"']['smudge'] == 'cat'
    assert re.match(r'.*python.* -m nbstripout -t', config['diff "ipynb"']['textconv'])


def test_install_different_python(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    assert pytester.run('nbstripout', '--is-installed').ret == 1
    pytester.run('nbstripout', '--install', '--python', 'DIFFERENTPYTHON')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    config = ConfigParser()
    config.read('.git/config')
    assert re.match(r'.*DIFFERENTPYTHON.* -m nbstripout', config['filter "nbstripout"']['clean'])
    assert sys.executable not in config['filter "nbstripout"']['clean']
    assert config['filter "nbstripout"']['required'] == 'true'
    assert config['filter "nbstripout"']['smudge'] == 'cat'
    assert re.match(r'.*DIFFERENTPYTHON.* -m nbstripout -t', config['diff "ipynb"']['textconv'])
    assert sys.executable not in config['diff "ipynb"']['textconv']


def test_uninstall(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    # add extra filter at the start, so we can check we don't remove it
    pytester.path.joinpath('.git/info/attributes').write_text('*.txt text')

    # do the install and verify
    pytester.run('nbstripout', '--install')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    # uninstall and verify (the actual test)
    pytester.run('nbstripout', '--uninstall')
    assert pytester.run('nbstripout', '--is-installed').ret == 1

    with open('.git/info/attributes', 'r') as f:
        attr_lines = f.readlines()
    assert '*.txt text\n' in attr_lines  # still there and not removed
    assert len(attr_lines) == 1

    config = ConfigParser()
    config.read('.git/config')
    assert 'filter "nbstripout"' not in config
    assert 'diff "ipynb"' not in config


def test_uninstall_leave_extrakeys(pytester: pytest.Pytester):
    pytester.run('git', 'init')

    # add extrakeys so we can check that we don't remove them
    pytester.run('git', 'config', 'filter.nbstripout.extrakeys', 'spam eggs')

    # check not installed
    assert pytester.run('nbstripout', '--is-installed').ret == 1

    # do the install and verify
    pytester.run('nbstripout', '--install')
    assert pytester.run('nbstripout', '--is-installed').ret == 0

    # uninstall and verify
    pytester.run('nbstripout', '--uninstall')
    assert pytester.run('nbstripout', '--is-installed').ret == 1

    # check extrakeys still exist
    r = pytester.run('git', 'config', 'filter.nbstripout.extrakeys')
    assert r.stdout.str() == 'spam eggs'


def test_status(pytester: pytest.Pytester):
    pytester.run('git', 'init')

    # status when not installed
    r = pytester.run('nbstripout', '--status')
    r.stdout.fnmatch_lines(['nbstripout is not installed in repository *'])
    assert r.ret == 1

    # do the install and verify
    pytester.run('nbstripout', '--install')
    r = pytester.run('nbstripout', '--status')
    assert r.ret == 0
    r.stdout.re_match_lines(
        r"""nbstripout is installed in repository .*
\s*
Filter:
  clean = .* -m nbstripout
  smudge = cat
  diff= .* -m nbstripout -t
  extrakeys=\s*
\s*
Attributes:
  \*.ipynb: filter: nbstripout
\s*
Diff Attributes:
  \*.ipynb: diff: ipynb
""".splitlines()
    )

    # uninstall and verify
    pytester.run('nbstripout', '--uninstall')
    r = pytester.run('nbstripout', '--status')
    r.stdout.fnmatch_lines(['nbstripout is not installed in repository *'])
    assert r.ret == 1


def test_git_diff_nodiff(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run('git', 'config', '--local', 'filter.nbstripout.extrakeys', ' ')
    pytester.run('nbstripout', '--install')

    r = pytester.run(
        'git',
        'diff',
        '--no-index',
        '--no-ext-diff',
        '--unified=0',
        '--exit-code',
        '-a',
        '--no-prefix',
        NOTEBOOKS_FOLDER / 'test_diff.ipynb',
        NOTEBOOKS_FOLDER / 'test_diff_output.ipynb',
    )
    assert r.ret == 0
    assert not r.outlines


def test_git_diff_diff(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run('git', 'config', '--local', 'filter.nbstripout.extrakeys', ' ')
    pytester.run('nbstripout', '--install')

    r = pytester.run(
        'git',
        'diff',
        '--no-index',
        NOTEBOOKS_FOLDER / 'test_diff.ipynb',
        NOTEBOOKS_FOLDER / 'test_diff_different_extrakeys.ipynb',
    )
    assert r.ret == 1
    r.stdout.fnmatch_lines(
        r"""index*
--- *test_diff.ipynb*
+++ *test_diff_different_extrakeys.ipynb*
@@ -6,15 +6,14 @@
    "metadata": {},
    "outputs": [],
    "source": [
-    "print(\"aou\")"
+    "print(\"aou now it is different\")"
    ]
   }
  ],
  "metadata": {
   "kernelspec": {
    "display_name": "Python 2",
-   "language": "python",
-   "name": "python2"
+   "language": "python"
   },
   "language_info": {
    "codemirror_mode": {
""".splitlines()
    )
    assert len(r.outlines) == 22  # 21 lines + new line at end


def test_git_diff_extrakeys(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run(
        'git', 'config', '--local', 'filter.nbstripout.extrakeys', 'cell.metadata.collapsed metadata.kernelspec.name'
    )
    pytester.run('nbstripout', '--install')

    r = pytester.run(
        'git',
        'diff',
        '--no-index',
        NOTEBOOKS_FOLDER / 'test_diff.ipynb',
        NOTEBOOKS_FOLDER / 'test_diff_different_extrakeys.ipynb',
    )
    assert r.ret == 1
    r.stdout.fnmatch_lines(
        r"""index*
--- *test_diff.ipynb*
+++ *test_diff_different_extrakeys.ipynb*
@@ -6,7 +6,7 @@
    "metadata": {},
    "outputs": [],
    "source": [
-    "print(\"aou\")"
+    "print(\"aou now it is different\")"
    ]
   }
  ],
""".splitlines()
    )
    assert len(r.outlines) == 13  # 12 lines + new line at end


def test_git_diff_keepmetadatakeys(pytester: pytest.Pytester):
    pytester.run('git', 'init')
    pytester.run(
        'git', 'config', '--local', 'filter.nbstripout.keepmetadatakeys', 'cell.metadata.scrolled metadata.foo.bar'
    )
    pytester.run('nbstripout', '--install')

    r = pytester.run(
        'git',
        'diff',
        '--no-index',
        NOTEBOOKS_FOLDER / 'test_diff.ipynb',
        NOTEBOOKS_FOLDER / 'test_diff_different_extrakeys.ipynb',
    )
    assert r.ret == 1
    r.stdout.fnmatch_lines(
        r"""index*
--- *test_diff.ipynb*
+++ *test_diff_different_extrakeys.ipynb*
@@ -3,20 +3,17 @@
   {
    "cell_type": "code",
    "execution_count": null,
-   "metadata": {
-    "scrolled": true
-   },
+   "metadata": {},
    "outputs": [],
    "source": [
-    "print(\"aou\")"
+    "print(\"aou now it is different\")"
    ]
   }
  ],
""".splitlines()
    )
    assert len(r.outlines) == 28  # 12 lines + new line at end
