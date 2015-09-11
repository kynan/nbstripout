nbstripout: strip outputs from an IPython Notebook
##################################################

Opens a notebook, strips its output, and writes the outputless version to the
original file.

Useful mainly as a git filter or pre-commit hook for users who don't want to
track output in VCS.

This does mostly the same thing as the `Clear All Output` command in the
notebook UI.

Usage
=====

Strip output from IPython / Jupyter notebook (modifies the file in-place): ::

    nbstripout FILE.ipynb

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
