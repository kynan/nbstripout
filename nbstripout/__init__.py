from ._nbstripout import __doc__ as docstring
from ._nbstripout import install, main, status, uninstall
from ._utils import MetadataError, pop_recursive, strip_output

__all__ = ['MetadataError', 'install', 'main', 'pop_recursive', 'status', 'strip_output', 'uninstall']
__doc__ = docstring
