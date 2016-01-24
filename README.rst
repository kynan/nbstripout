nbstripout: strip output from Jupyter and IPython notebooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Opens a notebook, strips its output, and writes the outputless version to the
original file.

Useful mainly as a git filter or pre-commit hook for users who don't want to
track output in VCS.

This does mostly the same thing as the `Clear All Output` command in the
notebook UI.

Based on https://gist.github.com/minrk/6176788.

Usage
=====

Strip output from IPython / Jupyter notebook (modifies the files in-place): ::

    nbstripout FILE.ipynb [FILE2.ipynb ...]

Force processing of non ``.ipynb`` files:

    nbstripout -f FILE.ipynb.bak

Use as part of a shell pipeline: ::

    FILE.ipynb | nbstripout > OUT.ipynb

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout install

Show this help page: ::

    nbstripout help

Manual filter installation
==========================

Set up a git filter using nbstripout as follows: ::

    git config filter.nbstripout.clean '/path/to/nbstripout'
    git config filter.nbstripout.smudge cat
    git config filter.nbstripout.required true

Create a file ``.gitattributes`` or ``.git/info/attributes`` with: ::

    *.ipynb filter=nbstripout

Mercurial usage
===============

Mercurial does not have the equivalent of smudge filters.  One can use
an encode/decode hook but this has some issues.  An alternative
solution is to provide a set of commands that first run `nbstripout`,
then perform there operations.  This is the approach of the
[`mmf-setup` package](https://pypi.python.org/pypi/mmf-setup) which
uses the 0.2.x branch of `nbstripout`:

* http://bitbucket.org/mforbes/mmf_setup
