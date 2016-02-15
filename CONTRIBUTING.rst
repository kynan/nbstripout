How to contribute
=================

Development of nbstripout happens on GitHub_ - `bug reports`_ and `pull
requests`_ welcome!

Releasing a new version
-----------------------

To simplify updating the version number consistently across different files
and creating the appropriate annotated tag, we use bumpversion_. For a new
patch release, run ::

    bumpversion patch

and for a minor release ::

    bumpversion minor

**Note:** bumpversion_ does not (as of 0.5.3) support creating annotated tags.
We therefore use a fork_ which you can install with ::

    pip install git+https://github.com/ekohl/bumpversion@annotated-tags

.. _GitHub: https://github.com/kynan/nbstripout
.. _bug reports: https://github.com/kynan/nbstripout/issues
.. _pull requests: https://github.com/kynan/nbstripout/pulls
.. _bumpversion: https://github.com/peritus/bumpversion
.. _fork: https://github.com/ekohl/bumpversion/tree/annotated-tags
