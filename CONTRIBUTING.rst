How to contribute
=================

Development of nbstripout happens on GitHub_ - `bug reports`_ and `pull
requests`_ welcome!

Releasing a new version
-----------------------

To simplify updating the version number consistently across different files
and creating the appropriate annotated tag, we use bump2version_. For a new
patch release, run ::

    bump2version patch

and for a minor release ::

    bump2version minor

Remember to also push the release tag with ``git push --tags``.

Use twine_ to upload the new release to PyPI.

.. _GitHub: https://github.com/kynan/nbstripout
.. _bug reports: https://github.com/kynan/nbstripout/issues
.. _pull requests: https://github.com/kynan/nbstripout/pulls
.. _bump2version: https://github.com/c4urself/bump2version
.. _twine: https://twine.readthedocs.io/en/latest/#using-twine
