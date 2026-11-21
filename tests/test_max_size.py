import nbformat
import pytest

from nbstripout import OutputTooLargeError, strip_output


@pytest.mark.parametrize('text_size', [7, 8, 9])
def test_max_size_error_boundary(text_size):
    output = nbformat.v4.new_output('stream', name='stdout', text='a' * text_size)
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(outputs=[output])])
    kwargs = {'keep_output': False, 'keep_count': False, 'keep_id': False, 'max_size': 20, 'max_size_action': 'error'}

    # 'stream' and 'stdout' contribute 12 characters, in addition to the text.
    if text_size > 8:
        with pytest.raises(OutputTooLargeError, match='cell number 1 has size 21, exceeding --max-size 20'):
            strip_output(nb, **kwargs)
        assert nb.cells[0].outputs == [output]
    else:
        assert strip_output(nb, **kwargs).cells[0].outputs == [output]


@pytest.mark.parametrize(
    'keep_output, keep_output_types, metadata',
    [
        (True, None, {}),
        (False, {'stream:stdout'}, {}),
        (None, None, {'keep_output': True}),
        (None, None, {'tags': ['keep_output']}),
        (None, None, {'init_cell': True}),
    ],
)
def test_max_size_error_respects_kept_output(keep_output, keep_output_types, metadata):
    output = nbformat.v4.new_output('stream', name='stdout', text='large output')
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(outputs=[output], metadata=metadata)])

    stripped = strip_output(
        nb,
        keep_output=keep_output,
        keep_count=False,
        keep_id=False,
        keep_output_types=keep_output_types,
        max_size=1,
        max_size_action='error',
    )

    assert stripped.cells[0].outputs == [output]
