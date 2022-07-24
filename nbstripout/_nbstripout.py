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

Strip output from IPython / Jupyter / Zeppelin notebook (modifies the file in-place): ::

    nbstripout <file.ipynb>
    nbstripout <file.zpln>

By default, nbstripout will only modify files ending in '.ipynb' or '.zpln', to
process other files us the '-f' flag to force the application.

    nbstripout -f <file.ipynb.bak>

For using Zeppelin mode while processing files with other extensions use:
    nbstripout -m zeppelin -f <file.ext>

Use as part of a shell pipeline: ::

    cat FILE.ipynb | nbstripout > OUT.ipynb
    cat FILE.zpln | nbstripout -m zeppelin > OUT.zpln

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout --install

Set up the git filter using ``.gitattributes`` ::

    nbstripout --install --attributes .gitattributes

Set up the git filter in your global ``~/.gitconfig`` ::

    nbstripout --install --global

Set up the git filter in your system-wide ``$(prefix)/etc/gitconfig`` (most installations will require you to ``sudo``) ::

    [sudo] nbstripout --install --system

Remove the git filter and attributes: ::

    nbstripout --uninstall

Remove the git filter from your global ``~/.gitconfig`` and attributes ::

    nbstripout --uninstall --global

Remove the git filter from your system-wide ``$(prefix)/etc/gitconfig`` and attributes ::

    nbstripout --uninstall --system

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

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import collections
import io
import json
from os import devnull, environ, makedirs, path
from pathlib import PureWindowsPath
import re
from subprocess import call, check_call, check_output, CalledProcessError, STDOUT
import sys
import warnings

from nbstripout._utils import strip_output, strip_zeppelin_output
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
__version__ = '0.6.0'


INSTALL_LOCATION_LOCAL = 'local'
INSTALL_LOCATION_GLOBAL = 'global'
INSTALL_LOCATION_SYSTEM = 'system'


def _get_system_gitconfig_folder():
    try:
        git_config_output = check_output(['git', 'config', '--system', '--list', '--show-origin'], universal_newlines=True, stderr=STDOUT).strip()

        # If the output is empty, it means the file exists but is empty, so we cannot get the path.
        # To still get it, we're setting a temporary config parameter.
        if git_config_output == '':
            check_call(['git', 'config', '--system', 'filter.nbstripoutput.test', 'test'])
            git_config_output = check_output(['git', 'config', '--system', '--list', '--show-origin'], universal_newlines=True).strip()
            check_call(['git', 'config', '--system', '--unset', 'filter.nbstripoutput.test'])

        output_lines = git_config_output.split('\n')

        system_gitconfig_file_path = re.sub(r'^file:', '', output_lines[0].split('\t')[0])
    except CalledProcessError as e:
        git_config_output = e.output

        system_gitconfig_file_path = re.match(r"fatal:.*file '([^']+)'.*", git_config_output).group(1)

    return path.abspath(path.dirname(system_gitconfig_file_path))


def _get_attrfile(git_config, install_location=INSTALL_LOCATION_LOCAL, attrfile=None):
    if not attrfile:
        if install_location == INSTALL_LOCATION_SYSTEM:
            try:
                attrfile = check_output(git_config + ['core.attributesFile'], universal_newlines=True).strip()
            except CalledProcessError:
                config_dir = _get_system_gitconfig_folder()
                attrfile = path.join(config_dir, 'gitattributes')
        elif install_location == INSTALL_LOCATION_GLOBAL:
            try:
                attrfile = check_output(git_config + ['core.attributesFile'], universal_newlines=True).strip()
            except CalledProcessError:
                config_dir = environ.get('XDG_CONFIG_DIR', path.expanduser('~/.config'))
                attrfile = path.join(config_dir, 'git', 'attributes')
        else:
            git_dir = check_output(['git', 'rev-parse', '--git-dir'], universal_newlines=True).strip()
            attrfile = path.join(git_dir, 'info', 'attributes')

    attrfile = path.expanduser(attrfile)
    if path.dirname(attrfile):
        makedirs(path.dirname(attrfile), exist_ok=True)

    return attrfile


def _parse_size(num_str):
    num_str = num_str.upper()
    if num_str[-1].isdigit():
        return int(num_str)
    elif num_str[-1] == 'K':
        return int(num_str[:-1]) * (10**3)
    elif num_str[-1] == 'M':
        return int(num_str[:-1]) * (10**6)
    elif num_str[-1] == 'G':
        return int(num_str[:-1]) * (10**9)
    else:
        raise ValueError(f"Unknown size identifier {num_str[-1]}")


def install(git_config, install_location=INSTALL_LOCATION_LOCAL, attrfile=None):
    """Install the git filter and set the git attributes."""
    try:
        filepath = f'"{PureWindowsPath(sys.executable).as_posix()}" -m nbstripout'
        check_call(git_config + ['filter.nbstripout.clean', filepath])
        check_call(git_config + ['filter.nbstripout.smudge', 'cat'])
        check_call(git_config + ['diff.ipynb.textconv', filepath + ' -t'])
        attrfile = _get_attrfile(git_config, install_location, attrfile)
    except FileNotFoundError:
        print('Installation failed: git is not on path!', file=sys.stderr)
        sys.exit(1)
    except CalledProcessError:
        print('Installation failed: not a git repository!', file=sys.stderr)
        sys.exit(1)

    # Check if there is already a filter for ipynb files
    filt_exists = False
    zeppelin_filt_exists = False
    diff_exists = False

    if path.exists(attrfile):
        with open(attrfile, 'r') as f:
            attrs = f.read()

        filt_exists = '*.ipynb filter' in attrs
        zeppelin_filt_exists = '*.zpln filter' in attrs
        diff_exists = '*.ipynb diff' in attrs

        if filt_exists and diff_exists:
            return

    try:
        with open(attrfile, 'a', newline='') as f:
            # If the file already exists, ensure it ends with a new line
            if f.tell():
                f.write('\n')
            if not filt_exists:
                print('*.ipynb filter=nbstripout', file=f)
            if not zeppelin_filt_exists:
                print('*.zpln filter=nbstripout', file=f)
            if not diff_exists:
                print('*.ipynb diff=ipynb', file=f)
    except PermissionError:
        print(f'Installation failed: could not write to {attrfile}', file=sys.stderr)

        if install_location == INSTALL_LOCATION_GLOBAL:
            print('Did you forget to sudo?', file=sys.stderr)

        sys.exit(1)


def uninstall(git_config, install_location=INSTALL_LOCATION_LOCAL, attrfile=None):
    """Uninstall the git filter and unset the git attributes."""
    try:
        call(git_config + ['--unset', 'filter.nbstripout.clean'], stdout=open(devnull, 'w'), stderr=STDOUT)
        call(git_config + ['--unset', 'filter.nbstripout.smudge'], stdout=open(devnull, 'w'), stderr=STDOUT)
        call(git_config + ['--remove-section', 'diff.ipynb'], stdout=open(devnull, 'w'), stderr=STDOUT)
        attrfile = _get_attrfile(git_config, install_location, attrfile)
    except FileNotFoundError:
        print('Uninstall failed: git is not on path!', file=sys.stderr)
        sys.exit(1)
    except CalledProcessError:
        print('Uninstall failed: not a git repository!', file=sys.stderr)
        sys.exit(1)

    # Check if there is a filter for ipynb files
    if path.exists(attrfile):
        with open(attrfile, 'r+') as f:
            patterns = ('*.ipynb filter', '*.zpln filter', '*.ipynb diff')
            lines = [line for line in f if not any(line.startswith(p) for p in patterns)]
            f.seek(0)
            f.write(''.join(lines))
            f.truncate()


def status(git_config, install_location=INSTALL_LOCATION_LOCAL, verbose=False):
    """Return 0 if nbstripout is installed in the current repo, 1 otherwise"""
    try:
        if install_location == INSTALL_LOCATION_SYSTEM:
            location = 'system-wide'
        elif install_location == INSTALL_LOCATION_GLOBAL:
            location = 'globally'
        else:
            git_dir = path.dirname(path.abspath(check_output(['git', 'rev-parse', '--git-dir'], universal_newlines=True).strip()))
            location = f"in repository '{git_dir}'"

        clean = check_output(git_config + ['filter.nbstripout.clean'], universal_newlines=True).strip()
        smudge = check_output(git_config + ['filter.nbstripout.smudge'], universal_newlines=True).strip()
        diff = check_output(git_config + ['diff.ipynb.textconv'], universal_newlines=True).strip()

        if install_location in {INSTALL_LOCATION_SYSTEM, INSTALL_LOCATION_GLOBAL}:
            attrfile = _get_attrfile(git_config, install_location)
            attributes = ''
            diff_attributes = ''

            if path.exists(attrfile):
                with open(attrfile, 'r') as f:
                    attrs = f.readlines()
                attributes = ''.join(line for line in attrs if 'filter' in line).strip()
                diff_attributes = ''.join(line for line in attrs if 'diff' in line).strip()
        else:
            attributes = check_output(['git', 'check-attr', 'filter', '--', '*.ipynb'], universal_newlines=True).strip()
            diff_attributes = check_output(['git', 'check-attr', 'diff', '--', '*.ipynb'], universal_newlines=True).strip()

        try:
            extra_keys = check_output(git_config + ['filter.nbstripout.extrakeys'], universal_newlines=True).strip()
        except CalledProcessError:
            extra_keys = ''

        if attributes.endswith('unspecified'):
            if verbose:
                print('nbstripout is not installed', location)

            return 1

        if verbose:
            print('nbstripout is installed', location)
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
    task.add_argument('--version', action='store_true',
                      help='Print version')
    parser.add_argument('--keep-count', action='store_true',
                        help='Do not strip the execution count/prompt number')
    parser.add_argument('--keep-output', action='store_true',
                        help='Do not strip output', default=None)
    parser.add_argument('--extra-keys', default='',
                        help='Space separated list of extra keys to strip '
                        'from metadata, e.g. metadata.foo cell.metadata.bar')
    parser.add_argument('--drop-empty-cells', action='store_true',
                        help='Remove cells where `source` is empty or contains only whitepace')
    parser.add_argument('--drop-tagged-cells', default='',
                        help='Space separated list of cell-tags that remove an entire cell')
    parser.add_argument('--strip-init-cells', action='store_true',
                        help='Remove cells with `init_cell: true` metadata (default: False)')
    parser.add_argument('--attributes', metavar='FILEPATH',
                        help='Attributes file to add the filter to (in '
                        'combination with --install/--uninstall), '
                        'defaults to .git/info/attributes')
    location = parser.add_mutually_exclusive_group()
    location.add_argument('--global', dest='_global', action='store_true',
                          help='Use global git config (default is local config)')
    location.add_argument('--system', dest='_system', action='store_true',
                          help='Use system git config (default is local config)')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Strip output also from files with non ipynb extension')
    parser.add_argument('--max-size', metavar='SIZE',
                        help='Keep outputs smaller than SIZE', default='0')
    parser.add_argument('--mode', '-m', default='jupyter', choices=['jupyter', 'zeppelin'],
                        help='Specify mode between [jupyter (default) | zeppelin] (to be used in combination with -f)')

    parser.add_argument('--textconv', '-t', action='store_true',
                        help='Prints stripped files to STDOUT')

    parser.add_argument('files', nargs='*', help='Files to strip output from')
    args = parser.parse_args()

    git_config = ['git', 'config']

    if args._system:
        git_config.append('--system')
        install_location = INSTALL_LOCATION_SYSTEM
    elif args._global:
        git_config.append('--global')
        install_location = INSTALL_LOCATION_GLOBAL
    else:
        git_config.append('--local')
        install_location = INSTALL_LOCATION_LOCAL

    if args.install:
        sys.exit(install(git_config, install_location, attrfile=args.attributes))
    if args.uninstall:
        sys.exit(uninstall(git_config, install_location, attrfile=args.attributes))
    if args.is_installed:
        sys.exit(status(git_config, install_location, verbose=False))
    if args.status:
        sys.exit(status(git_config, install_location, verbose=True))
    if args.version:
        print(__version__)
        sys.exit(0)

    extra_keys = [
        'metadata.signature',
        'metadata.widgets',
        'cell.metadata.collapsed',
        'cell.metadata.ExecuteTime',
        'cell.metadata.execution',
        'cell.metadata.heading_collapsed',
        'cell.metadata.hidden',
        'cell.metadata.scrolled',
    ]

    try:
        extra_keys.extend(check_output((git_config if args._system or args._global else ['git', 'config']) + ['filter.nbstripout.extrakeys'], universal_newlines=True).strip().split())
    except (CalledProcessError, FileNotFoundError):
        pass

    extra_keys.extend(args.extra_keys.split())

    # Wrap input/output stream in UTF-8 encoded text wrapper
    # https://stackoverflow.com/a/16549381
    input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8') if sys.stdin else None
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')

    for filename in args.files:
        if not (args.force or filename.endswith('.ipynb') or filename.endswith('.zpln')):
            continue

        try:
            with io.open(filename, 'r', encoding='utf8') as f:
                if args.mode == 'zeppelin' or filename.endswith('.zpln'):
                    if args.dry_run:
                        output_stream.write(f'Dry run: would have stripped {filename}\n')
                        continue
                    nb = json.load(f, object_pairs_hook=collections.OrderedDict)
                    nb_stripped = strip_zeppelin_output(nb)

                    with open(filename, 'w') as f:
                        json.dump(nb_stripped, f, indent=2)
                    continue
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=UserWarning)
                    nb = read(f, as_version=NO_CONVERT)

            nb = strip_output(nb, args.keep_output, args.keep_count, extra_keys, args.drop_empty_cells,
                              args.drop_tagged_cells.split(), args.strip_init_cells, _parse_size(args.max_size))

            if args.dry_run:
                output_stream.write(f'Dry run: would have stripped {filename}\n')

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
            print(f"'{filename}' is not a valid notebook", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"Could not strip '{filename}': file not found", file=sys.stderr)
            sys.exit(1)
        except Exception:
            # Ignore exceptions for non-notebook files.
            print(f"Could not strip '{filename}'", file=sys.stderr)
            raise

    if not args.files and input_stream:
        try:
            if args.mode == 'zeppelin':
                if args.dry_run:
                    output_stream.write('Dry run: would have stripped input from stdin\n')
                    sys.exit(0)
                nb = json.load(input_stream, object_pairs_hook=collections.OrderedDict)
                nb_stripped = strip_zeppelin_output(nb)
                json.dump(nb_stripped, output_stream, indent=2)
                output_stream.write('\n')
                output_stream.flush()
                sys.exit(0)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                nb = read(input_stream, as_version=NO_CONVERT)

            nb = strip_output(nb, args.keep_output, args.keep_count, extra_keys, args.drop_empty_cells,
                              args.drop_tagged_cells.split(), args.strip_init_cells, _parse_size(args.max_size))

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
