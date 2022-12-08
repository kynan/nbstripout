from argparse import ArgumentParser, Namespace, _StoreTrueAction, _StoreFalseAction
import os
import sys
from collections import defaultdict
from functools import partial
from typing import Any, Dict, Optional

__all__ = ["pop_recursive", "strip_output", "strip_zeppelin_output", "MetadataError"]


class MetadataError(Exception):
    pass


def pop_recursive(d, key, default=None):
    """dict.pop(key) where `key` is a `.`-delimited list of nested keys.

    >>> d = {'a': {'b': 1, 'c': 2}}
    >>> pop_recursive(d, 'a.c')
    2
    >>> d
    {'a': {'b': 1}}
    """
    if not isinstance(d, dict):
        return default
    if key in d:
        return d.pop(key, default)
    if '.' not in key:
        return default
    key_head, key_tail = key.split('.', maxsplit=1)
    if key_head in d:
        return pop_recursive(d[key_head], key_tail, default)
    return default


def _cells(nb, conditionals):
    """Remove cells not satisfying any conditional in conditionals and yield all other cells."""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for conditional in conditionals:
                ws.cells = list(filter(conditional, ws.cells))
            for cell in ws.cells:
                yield cell
    else:
        for conditional in conditionals:
            nb.cells = list(filter(conditional, nb.cells))
        for cell in nb.cells:
            yield cell


def get_size(item):
    """ Recursively sums length of all strings in `item` """
    if isinstance(item, str):
        return len(item)
    elif isinstance(item, list):
        return sum(get_size(elem) for elem in item)
    elif isinstance(item, dict):
        return get_size(list(item.values()))
    else:
        return len(str(item))


def determine_keep_output(cell, default, strip_init_cells=False):
    """Given a cell, determine whether output should be kept

    Based on whether the metadata has "init_cell": true,
    "keep_output": true, or the tags contain "keep_output" """
    if 'metadata' not in cell:
        return default
    if 'init_cell' in cell.metadata:
        return bool(cell.metadata.init_cell) and not strip_init_cells

    has_keep_output_metadata = 'keep_output' in cell.metadata
    keep_output_metadata = bool(cell.metadata.get('keep_output', False))

    has_keep_output_tag = 'keep_output' in cell.metadata.get('tags', [])

    # keep_output between metadata and tags should not contradict each other
    if has_keep_output_metadata and has_keep_output_tag and not keep_output_metadata:
        raise MetadataError(
            'cell metadata contradicts tags: `keep_output` is false, but `keep_output` in tags'
        )

    if has_keep_output_metadata or has_keep_output_tag:
        return keep_output_metadata or has_keep_output_tag
    return default


def _zeppelin_cells(nb):
    for pg in nb['paragraphs']:
        yield pg


def strip_zeppelin_output(nb):
    for cell in _zeppelin_cells(nb):
        if 'results' in cell:
            cell['results'] = {}
    return nb


def strip_output(nb, keep_output, keep_count, extra_keys=[], drop_empty_cells=False, drop_tagged_cells=[],
                 strip_init_cells=False, max_size=0):
    """
    Strip the outputs, execution count/prompt number and miscellaneous
    metadata from a notebook object, unless specified to keep either the outputs
    or counts.

    `extra_keys` could be 'metadata.foo cell.metadata.bar metadata.baz'
    """
    if keep_output is None and 'keep_output' in nb.metadata:
        keep_output = bool(nb.metadata['keep_output'])

    keys = defaultdict(list)
    for key in extra_keys:
        if '.' not in key or key.split('.')[0] not in ['cell', 'metadata']:
            sys.stderr.write(f'Ignoring invalid extra key `{key}`\n')
        else:
            namespace, subkey = key.split('.', maxsplit=1)
            keys[namespace].append(subkey)

    for field in keys['metadata']:
        pop_recursive(nb.metadata, field)

    conditionals = []
    # Keep cells if they have any `source` line that contains non-whitespace
    if drop_empty_cells:
        conditionals.append(lambda c: any(line.strip() for line in c.get('source', [])))
    for tag_to_drop in drop_tagged_cells:
        conditionals.append(lambda c: tag_to_drop not in c.get("metadata", {}).get("tags", []))

    for cell in _cells(nb, conditionals):
        keep_output_this_cell = determine_keep_output(cell, keep_output, strip_init_cells)

        # Remove the outputs, unless directed otherwise
        if 'outputs' in cell:

            # Default behavior (max_size == 0) strips all outputs.
            if not keep_output_this_cell:
                cell['outputs'] = [output for output in cell['outputs']
                                   if get_size(output) <= max_size]

            # Strip the counts from the outputs that were kept if not keep_count.
            if not keep_count:
                for output in cell['outputs']:
                    if 'execution_count' in output:
                        output['execution_count'] = None

            # If keep_output_this_cell and keep_count, do nothing.

        # Remove the prompt_number/execution_count, unless directed otherwise
        if 'prompt_number' in cell and not keep_count:
            cell['prompt_number'] = None
        if 'execution_count' in cell and not keep_count:
            cell['execution_count'] = None

        # Always remove some metadata
        for field in keys['cell']:
            pop_recursive(cell, field)
    return nb


def process_pyproject_toml(toml_file_path: str, parser: ArgumentParser) -> Optional[Dict[str, Any]]:
    """Extract config mapping from pyproject.toml file."""
    try:
        import tomllib  # python 3.11+
    except ModuleNotFoundError:
        import tomli as tomllib

    with open(toml_file_path, 'rb') as f:
        dict_config = tomllib.load(f).get('tool', {}).get('nbstripout', None)

    if not dict_config:
        # could be {} if 'tool' not found, or None if 'nbstripout' not found
        return dict_config

    # special processing of boolean options, make sure we don't have invalid types
    for a in parser._actions:
        if a.dest in dict_config and isinstance(a, (_StoreTrueAction, _StoreFalseAction)):
            if not isinstance(dict_config[a.dest], bool):
                raise ValueError(f'Argument {a.dest} in pyproject.toml must be a boolean, not {dict_config[a.dest]}')

    return dict_config


def process_setup_cfg(cfg_file_path, parser: ArgumentParser) -> Optional[Dict[str, Any]]:
    """Extract config mapping from setup.cfg file."""
    import configparser

    reader = configparser.ConfigParser()
    reader.read(cfg_file_path)
    if not reader.has_section('nbstripout'):
        return None

    raw_config = reader['nbstripout']
    dict_config = dict(raw_config)

    # special processing of boolean options, to convert various configparser bool types to true/false
    for a in parser._actions:
        if a.dest in raw_config and isinstance(a, (_StoreTrueAction, _StoreFalseAction)):
            dict_config[a.dest] = raw_config.getboolean(a.dest)

    return dict_config


def merge_configuration_file(parser: ArgumentParser, args_str=None) -> Namespace:
    """Merge flags from config files into args."""
    CONFIG_FILES = {
        'pyproject.toml': partial(process_pyproject_toml, parser=parser),
        'setup.cfg': partial(process_setup_cfg, parser=parser),
    }

    # parse args as-is to look for configuration files
    args = parser.parse_args(args_str)

    # Traverse the file tree common to all files given as argument looking for
    # a configuration file
    # TODO: make this more like Black:
    #       By default Black looks for pyproject.toml starting from the common base directory of all files and
    #       directories passed on the command line. If it’s not there, it looks in parent directories. It stops looking
    #       when it finds the file, or a .git directory, or a .hg directory, or the root of the file system, whichever
    #       comes first.
    # if no files are given, start from cwd
    config_path = os.path.commonpath([os.path.abspath(file) for file in args.files]) if args.files else os.path.abspath(os.getcwd())
    print(f"{config_path =}")
    config: Optional[Dict[str, Any]] = None
    while True:
        for config_file, processor in CONFIG_FILES.items():
            config_file_path = os.path.join(config_path, config_file)
            if os.path.isfile(config_file_path):
                config = processor(config_file_path)
                if config is not None:
                    break
        if config is not None:
            break
        config_path, tail = os.path.split(config_path)
        if not tail:
            break

    # black starts with default arguments (from click), updates that with the config file,
    # then applies command line arguments. this all happens in the click framework, before main() is called
    # we can use parser.set_defaults
    print(f'getting config {config}')
    if config:
        # check all arguments are valid
        print(f"have a config: {config.keys()}")
        valid_args = vars(args).keys()
        for name in config.keys():
            if name not in valid_args:
                raise ValueError(f'{name} in the config file is not a valid option')

        # separate into default-overrides and special treatment
        extra_keys: Optional[str] = None
        if 'extra_keys' in config:
            extra_keys = config['extra_keys']
            del config['extra_keys']

        # merge the configuration options as new defaults, and re-parse the arguments
        parser.set_defaults(**config)
        args = parser.parse_args(args_str)

        # merge extra_keys using set union
        if extra_keys:
            args.extra_keys = ' '.join(sorted(set(extra_keys.split()) | set(args.extra_keys.split())))

    return args
