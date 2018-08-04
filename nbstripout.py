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

Apply the filter for git diff of ``*.ipynb`` files: ::

    git config diff.ipynb.textconv '/path/to/nbstripout -t'

In file ``.gitattributes`` or ``.git/info/attributes`` add: ::

    *.ipynb diff=ipynb
"""

from __future__ import print_function
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import io
import sys

input_stream = None
if sys.version_info < (3, 0):
    import codecs
    # Use UTF8 reader/writer for stdin/stdout
    # http://stackoverflow.com/a/1169209
    if sys.stdin:
        input_stream = codecs.getreader('utf8')(sys.stdin)
    output_stream = codecs.getwriter('utf8')(sys.stdout)
else:
    # Wrap input/output stream in UTF-8 encoded text wrapper
    # https://stackoverflow.com/a/16549381
    if sys.stdin:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

__version__ = '0.3.3'

try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
    from nbformat.reader import NotJSONError
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
        from IPython.nbformat.reader import NotJSONError
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current
        from IPython.nbformat.reader import NotJSONError

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


def strip_output(nb, keep_output, keep_count):
    """
    Strip the outputs, execution count/prompt number and miscellaneous
    metadata from a notebook object, unless specified to keep either the outputs
    or counts.
    """

    nb.metadata.pop('signature', None)
    nb.metadata.pop('widgets', None)

    for cell in _cells(nb):

        keep_output_this_cell = keep_output

        # Keep the output for these cells, but strip count and metadata
        if cell.metadata.get('init_cell') or cell.metadata.get('keep_output'):
            keep_output_this_cell = True

        # Remove the outputs, unless directed otherwise
        if 'outputs' in cell:

            # Default behavior strips outputs. With all outputs stripped,
            # there are no counts to keep and keep_count is ignored.
            if not keep_output_this_cell:
                cell['outputs'] = []

            # If keep_output_this_cell, but not keep_count, strip the counts
            # from the output.
            if keep_output_this_cell and not keep_count:
                for output in cell['outputs']:
                    if 'execution_count' in output:
                        output['execution_count'] = None

            # If keep_output_this_cell and keep_count, do nothing.

        # Remove the prompt_number/execution_count, unless directed otherwise
        if 'prompt_number' in cell and not keep_count:
            cell['prompt_number'] = None
        if 'execution_count' in cell and not keep_count:
            cell['execution_count'] = None

        # Always remove this metadata
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
    except WindowsError:
        print('Installation failed: git is not on path!', file=sys.stderr)
        sys.exit(1)
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)
    filepath = '"%s" "%s"' % (sys.executable.replace('\\', '/'),
                              path.abspath(__file__).replace('\\', '/'))
    check_call(['git', 'config', 'filter.nbstripout.clean', filepath])
    check_call(['git', 'config', 'filter.nbstripout.smudge', 'cat'])
    check_call(['git', 'config', 'filter.nbstripout.required', 'true'])
    check_call(['git', 'config', 'diff.ipynb.textconv', filepath + ' -t'])

    if not attrfile:
        attrfile = path.join(git_dir.decode(), 'info', 'attributes')

    # Check if there is already a filter for ipynb files
    filt_exists = False
    diff_exists = False
    if path.exists(attrfile):
        with open(attrfile, 'r') as f:
            attrs = f.read()
        filt_exists = '*.ipynb filter' in attrs
        diff_exists = '*.ipynb diff' in attrs
        if filt_exists and diff_exists:
            return

    with open(attrfile, 'a') as f:
        if not filt_exists:
            print(('\n' if f.tell() else '') + '*.ipynb filter=nbstripout', file=f)
        if not diff_exists:
            print(('\n' if f.tell() else '') + '*.ipynb diff=ipynb', file=f)


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

    call(['git', 'config', '--remove-section', 'diff.ipynb'],
         stdout=open(devnull, 'w'), stderr=STDOUT)

    if not attrfile:
        attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    # Check if there is a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r+') as f:
            lines = [l for l in f if not (l.startswith('*.ipynb filter') or l.startswith('*.ipynb diff'))]
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
        diff = check_output(['git', 'config', 'diff.ipynb.textconv']).strip()
        attributes = check_output(['git', 'check-attr', 'filter', '--', '*.ipynb']).strip()
        diff_attributes = check_output(['git', 'check-attr', 'diff', '--', '*.ipynb']).strip()
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
            print('  diff=', diff)
            print('\nAttributes:\n ', attributes)
            print('\nDiff Attributes:\n ', diff_attributes)
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
    parser.add_argument('--keep-count', action='store_true',
                        help='Do not strip the execution count/prompt number')
    parser.add_argument('--keep-output', action='store_true',
                        help='Do not strip output')
    parser.add_argument('--attributes', metavar='FILEPATH', help="""Attributes
        file to add the filter to (in combination with --install/--uninstall),
        defaults to .git/info/attributes""")
    task.add_argument('--version', action='store_true',
                      help='Print version')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Strip output also from files with non ipynb extension')

    parser.add_argument('--textconv', '-t', action='store_true',
                        help='Prints stripped files to STDOUT')

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
            nb = strip_output(nb, args.keep_output, args.keep_count)
            if args.textconv:
                write(nb, output_stream)
                output_stream.flush()
            else:
                with io.open(filename, 'w', encoding='utf8') as f:
                    write(nb, f)
        except NotJSONError:
            print("'{}' is not a valid notebook".format(filename), file=sys.stderr)
            sys.exit(1)
        except Exception:
            # Ignore exceptions for non-notebook files.
            print("Could not strip '{}'".format(filename), file=sys.stderr)
            raise

    if not args.files and input_stream:
        try:
            nb = strip_output(read(input_stream, as_version=NO_CONVERT),
                              args.keep_output, args.keep_count)
            write(nb, output_stream)
            output_stream.flush()
        except NotJSONError:
            print('No valid notebook detected', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
