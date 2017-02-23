#!/usr/bin/env python
"""
Strip output from Jupyter and IPython notebooks
===============================================

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

    cat FILE.ipynb | nbstripout > OUT.ipynb

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout --install

Set up the git filter using ``.gitattributes`` ::

    nbstripout --install --attributes .gitattributes

Remove the git filter and attributes: ::

    nbstripout --uninstall

Remove the git filter and attributes from ``.gitattributes``: ::

    nbstripout --uninstall --attributes .gitattributes

Check if ``nbstripout`` is installed in the current repository
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --is-installed

Print status of ``nbstripout`` installation in the current repository and
configuration summary of filter and attributes if installed
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --status

Print the version: ::

    nbstripout --version

Show this help page: ::

    nbstripout --help

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
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import io
import sys

if sys.version_info < (3, 0):
    import codecs
    # Use UTF8 reader/writer for stdin/stdout
    # http://stackoverflow.com/a/1169209
    input_stream = codecs.getreader('utf8')(sys.stdin)
    output_stream = codecs.getwriter('utf8')(sys.stdout)
else:
    # Wrap input/output stream in UTF-8 encoded text wrapper
    # https://stackoverflow.com/a/16549381
    input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

__version__ = '0.3.0'

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

        # Dummy value, ignored anyway
        NO_CONVERT = None

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
    nb.metadata.pop('widgets', None)
    for cell in _cells(nb):
        if (cell.metadata.get('init_cell') or cell.metadata.get('keep_output')):
            # Leave these cells alone
            continue
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'prompt_number' in cell:
            cell['prompt_number'] = None
        if 'execution_count' in cell:
            cell['execution_count'] = None
        for output_style in ['collapsed', 'scrolled']:
            if output_style in cell.metadata:
                cell.metadata[output_style] = False
        if 'metadata' in cell:
            for field in ['collapsed', 'scrolled', 'ExecuteTime']:
                cell.metadata.pop(field, None)
    return nb


def install(attrfile=None):
    """Install the git filter and set the git attributes."""
    from os import path
    from subprocess import check_call, check_output, CalledProcessError
    try:
        git_dir = check_output(['git', 'rev-parse', '--git-dir']).strip()
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)
    check_call(['git', 'config', 'filter.nbstripout.clean', '"%s" "%s"' %
               (sys.executable.replace('\\', '/'),
                path.abspath(__file__).replace('\\', '/'))])
    check_call(['git', 'config', 'filter.nbstripout.smudge', 'cat'])
    check_call(['git', 'config', 'filter.nbstripout.required', 'true'])
    if not attrfile:
        attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    # Check if there is already a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r') as f:
            if '*.ipynb filter' in f.read():
                return
    with open(attrfile, 'a') as f:
        print(('\n' if f.tell() else '') + '*.ipynb filter=nbstripout', file=f)


def uninstall(attrfile=None):
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
    if not attrfile:
        attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    # Check if there is a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r+') as f:
            lines = [l for l in f if not l.startswith('*.ipynb filter')]
            f.seek(0)
            f.write(''.join(lines))
            f.truncate()


def status(verbose=False):
    """Return 0 if nbstripout is installed in the current repo, 1 otherwise"""
    from os import path
    from subprocess import check_output, CalledProcessError
    try:
        git_dir = path.dirname(path.abspath(check_output(['git', 'rev-parse', '--git-dir']).strip()))
        clean = check_output(['git', 'config', 'filter.nbstripout.clean']).strip()
        smudge = check_output(['git', 'config', 'filter.nbstripout.smudge']).strip()
        required = check_output(['git', 'config', 'filter.nbstripout.required']).strip()
        attributes = check_output(['git', 'check-attr', 'filter', '--', '*.ipynb']).strip()
        if attributes.endswith(b'unspecified'):
            if verbose:
                print('nbstripout is not installed in repository', git_dir)
            return 1
        if verbose:
            print('nbstripout is installed in repository', git_dir)
            print('\nFilter:')
            print('  clean =', clean)
            print('  smudge =', smudge)
            print('  required =', required)
            print('\nAttributes:\n ', attributes)
        return 0
    except CalledProcessError:
        if verbose and 'git_dir' in locals():
            print('nbstripout is not installed in repository', git_dir)
        return 1


def main():
    parser = ArgumentParser(epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)
    task = parser.add_mutually_exclusive_group()
    task.add_argument('--install', action='store_true',
                      help="""Install nbstripout in the current repository (set
                              up the git filter and attributes)""")
    task.add_argument('--uninstall', action='store_true',
                      help="""Uninstall nbstripout from the current repository
                              (remove the git filter and attributes)""")
    task.add_argument('--is-installed', action='store_true',
                      help='Check if nbstripout is installed in current repository')
    task.add_argument('--status', action='store_true',
                      help='Print status of nbstripout installation in current repository and configuration summary if installed')
    parser.add_argument('--attributes', metavar='FILEPATH', help="""Attributes
        file to add the filter to (in combination with --install/--uninstall),
        defaults to .git/info/attributes""")
    task.add_argument('--version', action='store_true',
                      help='Print version')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Strip output also from files with non ipynb extension')
    parser.add_argument('files', nargs='*', help='Files to strip output from')
    args = parser.parse_args()

    if args.install:
        sys.exit(install(args.attributes))
    if args.uninstall:
        sys.exit(uninstall(args.attributes))
    if args.is_installed:
        sys.exit(status(verbose=False))
    if args.status:
        sys.exit(status(verbose=True))
    if args.version:
        print(__version__)
        sys.exit(0)

    for filename in args.files:
        if not (args.force or filename.endswith('.ipynb')):
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
    if not args.files:
        write(strip_output(read(input_stream, as_version=NO_CONVERT)), output_stream)


if __name__ == '__main__':
    main()
