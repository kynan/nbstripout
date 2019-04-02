from ._nbstripout import install, uninstall, status, main, __doc__ as docstring
from ._utils import pop_recursive, strip_output
__all__ = ["install", "uninstall", "status", "main",
           "pop_recursive", "strip_output"]
__doc__ = docstring
