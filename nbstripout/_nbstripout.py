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

Set up the git filter in your global ``~/.gitconfig`` ::

    nbstripout --install --global

Remove the git filter and attributes: ::

    nbstripout --uninstall

Remove the git filter from your global ``~/.gitconfig`` and attributes ::

    nbstripout --install --global

Remove the git filter and attributes from ``.gitattributes``: ::

    nbstripout --uninstall --attributes .gitattributes

Check if ``nbstripout`` is installed in the current repository
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --is-installed

Print status of ``nbstripout`` installation in the current repository and
configuration summary of filter and attributes if installed
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --status

Do a dry run and only list which files would have been stripped: ::

    nbstripout --dry-run FILE.ipynb [FILE2.ipynb ...]

Print the version: ::

    nbstripout --version

Show this help page: ::

    nbstripout --help

Manual filter installation
==========================

Set up a git filter using nbstripout as follows: ::

    git config filter.nbstripout.clean '/path/to/nbstripout'
    git config filter.nbstripout.smudge cat

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
from os import devnull, environ, path
from subprocess import call, check_call, check_output, CalledProcessError, STDOUT
import sys
import warnings
# warnings.simplefilter("ignore")

from nbstripout._utils import strip_output
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

__all__ = ["install", "uninstall", "status", "main"]
__version__ = '0.3.9'


def _get_attrfile(git_config, user=False, attrfile=None):
    if user and not attrfile:
        try:
            attrfile = check_output(git_config + ['core.attributesFile']).strip()
        except CalledProcessError:
            config_dir = environ.get('XDG_CONFIG_DIR', path.join(environ['HOME'], '.config'))
            attrfile = path.join(config_dir, 'git', 'attributes')
    elif not attrfile:
        git_dir = check_output(['git', 'rev-parse', '--git-dir']).strip()
        attrfile = path.join(git_dir.decode(), 'info', 'attributes')
    return path.expanduser(attrfile)


def install(git_config, user=False, attrfile=None):
    """Install the git filter and set the git attributes."""
    try:
        filepath = '"{}" -m nbstripout'.format(sys.executable.replace('\\', '/'))
        check_call(git_config + ['filter.nbstripout.clean', filepath])
        check_call(git_config + ['filter.nbstripout.smudge', 'cat'])
        check_call(git_config + ['diff.ipynb.textconv', filepath + ' -t'])
        attrfile = _get_attrfile(git_config, user, attrfile)
    except FileNotFoundError:
        print('Installation failed: git is not on path!', file=sys.stderr)
        sys.exit(1)
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)

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

    with open(attrfile, 'a', newline='') as f:
        # If the file already exists, ensure it ends with a new line
        if f.tell():
            f.write('\n')
        if not filt_exists:
            print('*.ipynb filter=nbstripout', file=f)
        if not diff_exists:
            print('*.ipynb diff=ipynb', file=f)


def uninstall(git_config, user=False, attrfile=None):
    """Uninstall the git filter and unset the git attributes."""
    try:
        call(git_config + ['--unset', 'filter.nbstripout.clean'], stdout=open(devnull, 'w'), stderr=STDOUT)
        call(git_config + ['--unset', 'filter.nbstripout.smudge'], stdout=open(devnull, 'w'), stderr=STDOUT)
        call(git_config + ['--remove-section', 'diff.ipynb'], stdout=open(devnull, 'w'), stderr=STDOUT)
        attrfile = _get_attrfile(git_config, user, attrfile)
    except FileNotFoundError:
        print('Uninstall failed: git is not on path!', file=sys.stderr)
        sys.exit(1)
    except CalledProcessError:
        print('Uninstall failed: not a git repository!', file=sys.stderr)
        sys.exit(1)

    # Check if there is a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r+') as f:
            lines = [line for line in f if not (line.startswith('*.ipynb filter') or line.startswith('*.ipynb diff'))]
            f.seek(0)
            f.write(''.join(lines))
            f.truncate()


def status(git_config, user=False, verbose=False):
    """Return 0 if nbstripout is installed in the current repo, 1 otherwise"""
    try:
        if user:
            location = 'globally'
        else:
            git_dir = path.dirname(path.abspath(check_output(['git', 'rev-parse', '--git-dir']).strip()))
            location = "in repository '{}'".format(git_dir)
        clean = check_output(git_config + ['filter.nbstripout.clean']).strip()
        smudge = check_output(git_config + ['filter.nbstripout.smudge']).strip()
        diff = check_output(git_config + ['diff.ipynb.textconv']).strip()
        if user:
            attrfile = _get_attrfile(git_config, user)
            attributes = ''
            diff_attributes = ''
            if path.exists(attrfile):
                with open(attrfile, 'r') as f:
                    attrs = f.readlines()
                attributes = ''.join(line for line in attrs if 'filter' in line).strip()
                diff_attributes = ''.join(line for line in attrs if 'diff' in line).strip()
        else:
            attributes = check_output(['git', 'check-attr', 'filter', '--', '*.ipynb']).strip()
            diff_attributes = check_output(['git', 'check-attr', 'diff', '--', '*.ipynb']).strip()
        try:
            extra_keys = check_output(git_config + ['filter.nbstripout.extrakeys']).strip()
        except CalledProcessError:
            extra_keys = ''
        if attributes.endswith(b'unspecified'):
            if verbose:
                print('nbstripout is not installed', location)
            return 1
        if verbose:
            print('nbstripout is installed', git_dir)
            print('\nFilter:')
            print('  clean =', clean)
            print('  smudge =', smudge)
            print('  diff=', diff)
            print('  extrakeys=', extra_keys)
            print('\nAttributes:\n ', attributes)
            print('\nDiff Attributes:\n ', diff_attributes)
        return 0
    except FileNotFoundError:
        print('Cannot determine status: git is not on path!', file=sys.stderr)
        return 1
    except CalledProcessError:
        if verbose and 'location' in locals():
            print('nbstripout is not installed', location)
        return 1


def main():
    parser = ArgumentParser(epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)
    task = parser.add_mutually_exclusive_group()
    task.add_argument('--dry-run', action='store_true',
                      help='Print which notebooks would have been stripped')
    task.add_argument('--install', action='store_true',
                      help='Install nbstripout in the current repository (set '
                      'up the git filter and attributes)')
    task.add_argument('--uninstall', action='store_true',
                      help='Uninstall nbstripout from the current repository '
                      '(remove the git filter and attributes)')
    task.add_argument('--is-installed', action='store_true',
                      help='Check if nbstripout is installed in current repository')
    task.add_argument('--status', action='store_true',
                      help='Print status of nbstripout installation in current '
                      'repository and configuration summary if installed')
    parser.add_argument('--keep-count', action='store_true',
                        help='Do not strip the execution count/prompt number')
    parser.add_argument('--keep-output', action='store_true',
                        help='Do not strip output', default=None)
    parser.add_argument('--extra-keys', default='',
                        help='Extra keys to strip from metadata, e.g. metadata.foo cell.metadata.bar')
    parser.add_argument('--attributes', metavar='FILEPATH',
                        help='Attributes file to add the filter to (in '
                        'combination with --install/--uninstall), '
                        'defaults to .git/info/attributes')
    parser.add_argument('--global', dest='_global', action='store_true',
                        help='Use global git config (default is local config)')
    task.add_argument('--version', action='store_true',
                      help='Print version')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Strip output also from files with non ipynb extension')

    parser.add_argument('--textconv', '-t', action='store_true',
                        help='Prints stripped files to STDOUT')

    parser.add_argument('files', nargs='*', help='Files to strip output from')
    args = parser.parse_args()

    git_config = ['git', 'config'] + (['--global'] if args._global else [])
    if args.install:
        sys.exit(install(git_config, user=args._global, attrfile=args.attributes))
    if args.uninstall:
        sys.exit(uninstall(git_config, user=args._global, attrfile=args.attributes))
    if args.is_installed:
        sys.exit(status(git_config, user=args._global, verbose=False))
    if args.status:
        sys.exit(status(git_config, user=args._global, verbose=True))
    if args.version:
        print(__version__)
        sys.exit(0)

    try:
        extra_keys = check_output(git_config + ['filter.nbstripout.extrakeys']).strip()
        if args.extra_keys:
            extra_keys = ' '.join((extra_keys, args.extra_keys))
    except (CalledProcessError, FileNotFoundError):
        extra_keys = args.extra_keys

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
        output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')

    for filename in args.files:
        if not (args.force or filename.endswith('.ipynb')):
            continue
        try:
            with io.open(filename, 'r', encoding='utf8') as f:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    nb = read(f, as_version=NO_CONVERT)
            nb = strip_output(nb, args.keep_output, args.keep_count, extra_keys)
            if args.dry_run:
                output_stream.write('Dry run: would have stripped {}\n'.format(
                    filename))
                continue
            if args.textconv:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    write(nb, output_stream)
                output_stream.flush()
            else:
                with io.open(filename, 'w', encoding='utf8', newline='') as f:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=UserWarning)
                        write(nb, f)
        except NotJSONError:
            print("'{}' is not a valid notebook".format(filename), file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Could not strip '{}': file not found".format(filename), file=sys.stderr)
            sys.exit(1)
        except Exception:
            # Ignore exceptions for non-notebook files.
            print("Could not strip '{}'".format(filename), file=sys.stderr)
            raise

    if not args.files and input_stream:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                nb = read(input_stream, as_version=NO_CONVERT)
            nb = strip_output(nb, args.keep_output, args.keep_count, extra_keys)
            if args.dry_run:
                output_stream.write('Dry run: would have stripped input from '
                                    'stdin\n')
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    write(nb, output_stream)
                output_stream.flush()
        except NotJSONError:
            print('No valid notebook detected', file=sys.stderr)
            sys.exit(1)
