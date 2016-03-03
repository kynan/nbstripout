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

By default, nbstripout will only modify files ending in '.ipynb', to
process other files us the '-f' flag to force the application.

    nbstripout -f <file.ipynb.bak>

Use as part of a shell pipeline: ::

    FILE.ipynb | nbstripout > OUT.ipynb

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout install

Remove the git filter and attributes: ::

    nbstripout uninstall

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
import codecs
import io
import sys

if sys.version_info < (3, 0):
    # Use UTF8 writer for stdout (http://stackoverflow.com/a/1169209)
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

__version__ = '0.2.5'

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
        if 'execution_count' in cell:
            cell['execution_count'] = None
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
    check_call(['git', 'config', 'filter.nbstripout.clean', '%s %s' %
               (sys.executable.replace('\\', '/'),
                path.abspath(__file__).replace('\\', '/'))])
    check_call(['git', 'config', 'filter.nbstripout.smudge', 'cat'])
    check_call(['git', 'config', 'filter.nbstripout.required', 'true'])
    attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    # Check if there is already a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r') as f:
            if '*.ipynb filter' in f.read():
                return
    with open(attrfile, 'a') as f:
        f.write('\n*.ipynb filter=nbstripout')


def uninstall():
    """Uninstall the git filter and unset the git attributes."""
    from os import devnull, path
    from subprocess import call, check_output, CalledProcessError, STDOUT
    try:
        git_dir = check_output(['git', 'rev-parse', '--git-dir']).strip()
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)
    call(['git', 'config', '--remove-section', 'filter.nbstripout'],
         stdout=open(devnull, 'w'), stderr=STDOUT)
    attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    # Check if there is a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r') as f:
            if '*.ipynb filter' not in f.read():
                return
        with open(attrfile, 'w+') as f:
            f.write(''.join(l for l in f if '*.ipynb filter' not in l))


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['help', '-h', '--help']:
            print(__doc__, file=sys.stderr)
            sys.exit(1)
        if sys.argv[1] in ['install', '--install']:
            sys.exit(install())
        if sys.argv[1] in ['uninstall', '--uninstall']:
            sys.exit(uninstall())
        if sys.argv[1] in ['version', '--version']:
            print(__version__)
            sys.exit(0)

        force = False
        filenames = sys.argv[1:]
        if filenames[0] in ['-f', '--force']:
            force = True
            filenames.pop(0)

        for filename in filenames:
            if not force and not filename.endswith('.ipynb'):
                continue
            try:
                with io.open(filename, 'r', encoding='utf8') as f:
                    nb = read(f, as_version=NO_CONVERT)
                nb = strip_output(nb)
                with io.open(filename, 'w', encoding='utf8') as f:
                    write(nb, f)
            except Exception:
                # Ignore exceptions for non-notebook files.
                print("Could not strip '{}'".format(filename))
                raise
    else:
        write(strip_output(read(sys.stdin, as_version=NO_CONVERT)), sys.stdout)

if __name__ == '__main__':
    main()
