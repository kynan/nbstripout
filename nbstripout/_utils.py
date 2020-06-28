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
    nested = key.split('.')
    current = d
    for k in nested[:-1]:
        if hasattr(current, 'get'):
            current = current.get(k, {})
        else:
            return default
    if not hasattr(current, 'pop'):
        return default
    return current.pop(nested[-1], default)


def _cells(nb):
    """Yield all cells in an nbformat-insensitive manner"""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for cell in ws.cells:
                yield cell
    else:
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
            "cell metadata contradicts tags: "
            "\"keep_output\": false, but keep_output in tags"
        )

    if has_keep_output_metadata or has_keep_output_tag:
        return keep_output_metadata or has_keep_output_tag
    return default


def strip_output(nb, keep_output, keep_count, extra_keys=''):
    """
    Strip the outputs, execution count/prompt number and miscellaneous
    metadata from a notebook object, unless specified to keep either the outputs
    or counts.

    `extra_keys` could be 'metadata.foo cell.metadata.bar metadata.baz'
    """
    if keep_output is None and 'keep_output' in nb.metadata:
        keep_output = bool(nb.metadata['keep_output'])

    if hasattr(extra_keys, 'decode'):
        extra_keys = extra_keys.decode()
    extra_keys = extra_keys.split()
    keys = {'metadata': [], 'cell': {'metadata': []}}
    for key in extra_keys:
        if key.startswith('metadata.'):
            keys['metadata'].append(key[len('metadata.'):])
        elif key.startswith('cell.metadata.'):
            keys['cell']['metadata'].append(key[len('cell.metadata.'):])
        else:
            sys.stderr.write('ignoring extra key `%s`' % key)

    nb.metadata.pop('signature', None)
    nb.metadata.pop('widgets', None)

    for field in keys['metadata']:
        pop_recursive(nb.metadata, field)

    for cell in _cells(nb):
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
        if 'metadata' in cell:
            for output_style in ['collapsed', 'scrolled']:
                if output_style in cell.metadata:
                    cell.metadata[output_style] = False
            for field in ['ExecuteTime', 'collapsed', 'execution', 'scrolled']:
                cell.metadata.pop(field, None)
        for (extra, fields) in keys['cell'].items():
            if extra in cell:
                for field in fields:
                    pop_recursive(getattr(cell, extra), field)
    return nb
