How to contribute
=================

Development of nbstripout happens on GitHub_ - `bug reports`_ and `pull
requests`_ welcome!

Releasing a new version
-----------------------

To simplify updating the version number consistently across different files
and creating the appropriate annotated tag, we use bump-my-version_. For a new
patch release, run ::

    bump-my-version bump patch

and for a minor release ::

    bump-my-version bump minor

Remember to also push the release tag with ``git push --tags``.

Use twine_ to upload the new release to PyPI.

.. _GitHub: https://github.com/kynan/nbstripout
.. _bug reports: https://github.com/kynan/nbstripout/issues
.. _pull requests: https://github.com/kynan/nbstripout/pulls
.. _bump-my-version: https://github.com/callowayproject/bump-my-version
.. _twine: https://twine.readthedocs.io/en/latest/#using-twine
