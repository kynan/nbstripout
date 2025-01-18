from collections import defaultdict
import sys
from typing import Any, Callable, Iterator, List, Optional

from nbformat import NotebookNode

__all__ = ['pop_recursive', 'strip_output', 'strip_zeppelin_output', 'MetadataError']


class MetadataError(Exception):
    pass


def pop_recursive(d: dict, key: str, default: Optional[NotebookNode] = None) -> NotebookNode:
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
        return pop_recursive(d[key_head], key=key_tail, default=default)
    return default


def _cells(nb: NotebookNode, conditionals: Callable[[NotebookNode], bool]) -> Iterator[NotebookNode]:
    """Remove cells not satisfying any conditional in conditionals and yield all other cells."""
    if hasattr(nb, 'nbformat') and nb.nbformat < 4:
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


def get_size(item: Any) -> int:
    """Recursively sums length of all strings in `item`"""
    if isinstance(item, str):
        return len(item)
    elif isinstance(item, list):
        return sum(get_size(elem) for elem in item)
    elif isinstance(item, dict):
        return get_size(list(item.values()))
    else:
        return len(str(item))


def determine_keep_output(cell: NotebookNode, default: bool, strip_init_cells: bool = False):
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
        raise MetadataError('cell metadata contradicts tags: `keep_output` is false, but `keep_output` in tags')

    if has_keep_output_metadata or has_keep_output_tag:
        return keep_output_metadata or has_keep_output_tag
    return default


def _zeppelin_cells(nb: dict) -> Iterator[dict]:
    for pg in nb['paragraphs']:
        yield pg


def strip_zeppelin_output(nb: dict) -> dict:
    for cell in _zeppelin_cells(nb):
        if 'results' in cell:
            cell['results'] = {}
    return nb


def strip_output(
    nb: NotebookNode,
    keep_output: bool,
    keep_count: bool,
    keep_id: bool,
    extra_keys: List[str] = [],
    drop_empty_cells: bool = False,
    drop_tagged_cells: List[str] = [],
    strip_init_cells: bool = False,
    max_size: int = 0,
) -> NotebookNode:
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
        pop_recursive(nb.metadata, key=field)

    conditionals = []
    # Keep cells if they have any `source` line that contains non-whitespace
    if drop_empty_cells:
        conditionals.append(lambda c: any(line.strip() for line in c.get('source', [])))
    for tag_to_drop in drop_tagged_cells:
        conditionals.append(lambda c: tag_to_drop not in c.get('metadata', {}).get('tags', []))

    for i, cell in enumerate(_cells(nb, conditionals)):
        keep_output_this_cell = determine_keep_output(cell=cell, default=keep_output, strip_init_cells=strip_init_cells)

        # Remove the outputs, unless directed otherwise
        if 'outputs' in cell:
            # Default behavior (max_size == 0) strips all outputs.
            if not keep_output_this_cell:
                cell['outputs'] = [output for output in cell['outputs'] if get_size(output) <= max_size]

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
        # Replace the cell id with an incremental value that will be consistent across runs
        if 'id' in cell and not keep_id:
            cell['id'] = str(i)
        for field in keys['cell']:
            pop_recursive(cell, key=field)
    return nb
