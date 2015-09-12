#!/usr/bin/env python
"""nbstripout: strip output from Jupyter and IPython notebooks

Opens a notebook, strips its output, and writes the outputless version to the
original file.

Useful mainly as a git filter or pre-commit hook for users who don't want to
track output in VCS.

This does mostly the same thing as the `Clear All Output` command in the
notebook UI.

Usage
=====

Strip output from IPython / Jupyter notebook (modifies the file in-place): ::

    nbstripout <file.ipynb>

Use as part of a shell pipeline: ::

    FILE.ipynb | nbstripout > OUT.ipynb

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout install

Show this help page: ::

    nbstripout help

Manual filter installation
==========================

Set up a git filter using nbstripout as follows: ::

    git config filter.nbstripout.clean '/path/to/nbstripout'
    git config filter.nbstripout.smudge cat
    git config filter.nbstripout.required true

Create a file ``.gitattributes`` or ``.git/info/attributes`` with: ::

    *.ipynb filter=nbstripout
"""

from __future__ import print_function
import io
import sys

try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current

        def read(f, as_version):
            return current.read(f, 'json')

        def write(nb, f):
            return current.write(nb, f, 'json')


def _cells(nb):
    """Yield all cells in an nbformat-insensitive manner"""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for cell in ws.cells:
                yield cell
    else:
        for cell in nb.cells:
            yield cell


def strip_output(nb):
    """strip the outputs from a notebook object"""
    nb.metadata.pop('signature', None)
    for cell in _cells(nb):
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'prompt_number' in cell:
            cell['prompt_number'] = None
    return nb


def install():
    """Install the git filter and set the git attributes."""
    from os import path
    from subprocess import check_call, check_output, CalledProcessError
    try:
        git_dir = check_output(['git', 'rev-parse', '--git-dir']).strip()
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)
    check_call(['git', 'config', 'filter.nbstripout.clean', "'%s'" % path.abspath(__file__)])
    check_call(['git', 'config', 'filter.nbstripout.smudge', 'cat'])
    check_call(['git', 'config', 'filter.nbstripout.required', 'true'])
    with open(path.join(git_dir, 'info', 'attributes'), 'a') as f:
        f.write('\n*.ipynb filter=nbstripout')


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['help', '-h', '--help']:
            print(__doc__, file=sys.stderr)
            sys.exit(1)
        if sys.argv[1] in ['install', '--install']:
            sys.exit(install())
        filename = sys.argv[1]
        with io.open(filename, 'r', encoding='utf8') as f:
            nb = read(f, as_version=NO_CONVERT)
        nb = strip_output(nb)
        with io.open(filename, 'w', encoding='utf8') as f:
            write(nb, f)
    else:
        write(strip_output(read(sys.stdin, as_version=NO_CONVERT)), sys.stdout)

if __name__ == '__main__':
    main()
