from collections import defaultdict
import sys

__all__ = ["pop_recursive", "strip_output", "MetadataError"]


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


def _cells(nb, conditional=None):
    """Remove cells not satisfying conditional and yield all other cells."""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            if conditional:
                ws.cells = list(filter(conditional, ws.cells))
            for cell in ws.cells:
                yield cell
    else:
        if conditional:
            nb.cells = list(filter(conditional, nb.cells))
        for cell in nb.cells:
            yield cell


def determine_keep_output(cell, default):
    """Given a cell, determine whether output should be kept

    Based on whether the metadata has "init_cell": true,
    "keep_output": true, or the tags contain "keep_output" """
    if 'metadata' not in cell:
        return default
    if 'init_cell' in cell.metadata:
        return bool(cell.metadata.init_cell)

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


def strip_output(nb, keep_output, keep_count, extra_keys=[], strip_empty_cells=False):
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
            sys.stderr.write('Ignoring invalid extra key `%s`\n' % key)
        else:
            namespace, subkey = key.split('.', maxsplit=1)
            keys[namespace].append(subkey)

    for field in keys['metadata']:
        pop_recursive(nb.metadata, field)

    # Keep cells if they have any `source` line that contains non-whitespace
    if strip_empty_cells:
        def conditional(cell):
            return any(line.strip() for line in cell.get('source', []))
    # Keep all cells
    else:
        conditional = None

    for cell in _cells(nb, conditional):
        keep_output_this_cell = determine_keep_output(cell, keep_output)

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

        # Always remove some metadata
        for field in keys['cell']:
            pop_recursive(cell, field)
    return nb
