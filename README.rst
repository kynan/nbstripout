.. image:: https://travis-ci.org/kynan/nbstripout.svg?branch=master
    :target: https://travis-ci.org/kynan/nbstripout
.. image:: https://img.shields.io/pypi/dm/nbstripout.svg
    :target: https://pypi.python.org/pypi/nbstripout
.. image:: https://img.shields.io/pypi/v/nbstripout.svg
    :target: https://pypi.python.org/pypi/nbstripout
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/kynan/nbstripout/master/LICENSE.txt
.. image:: https://img.shields.io/pypi/pyversions/nbstripout.svg
    :target: https://pypi.python.org/pypi/nbstripout

nbstripout: strip output from Jupyter and IPython notebooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Opens a notebook, strips its output, and writes the outputless version to the
original file.

Useful mainly as a git filter or pre-commit hook for users who don't want to
track output in VCS.

This does mostly the same thing as the `Clear All Output` command in the
notebook UI.

Based on https://gist.github.com/minrk/6176788.

Screencast
==========

This screencast demonstrates the use and working principles behind the
nbstripout utility and how to use it as a Git filter:

.. image:: http://i.imgur.com/7oQHuJ5.png
    :target: https://www.youtube.com/watch?v=BEMP4xacrVc

Installation
============

You can download and install the latest version of ``nbstripout`` from PyPI_,
the Python package index, as follows: ::

    pip install --upgrade nbstripout

When using the Anaconda_ Python distribution, install ``nbstripout`` via the
conda_ package manager from conda-forge_: ::

    conda install -c conda-forge nbstripout

Usage
=====

Strip output from IPython / Jupyter notebook (modifies the files in-place): ::

    nbstripout FILE.ipynb [FILE2.ipynb ...]

Force processing of non ``.ipynb`` files: ::

    nbstripout -f FILE.ipynb.bak

Use as part of a shell pipeline: ::

    FILE.ipynb | nbstripout > OUT.ipynb

Set up the git filter and attributes as described in the manual installation
instructions below: ::

    nbstripout --install

Set up the git filter using ``.gitattributes`` ::

    nbstripout --install --attributes .gitattributes

Remove the git filter and attributes: ::

    nbstripout --uninstall

Remove the git filter and attributes from ``.gitattributes``: ::

    nbstripout --uninstall --attributes .gitattributes

Check if ``nbstripout`` is installed in the current repository
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --is-installed

Print status of ``nbstripout`` installation in the current repository and
configuration summary of filter and attributes if installed
(exits with code 0 if installed, 1 otherwise): ::

    nbstripout --status

Print the version: ::

    nbstripout --version

Show this help page: ::

    nbstripout --help

Keeping some output
+++++++++++++++++++

To mark special cells so that the output is not striped, set the
``"keep_output": true`` metadata on the cell.  To do this, select the
"Edit Metadata" Cell Toolbar, and then use the "Edit Metadata" button
on the desired cell to enter something like::

    {
      "keep_output": true,
    }

Another use-case is to preserve initialization cells that might load
customized CSS etc. critical for the display of the notebook.  To
support this, we also keep output for cells with::

    {
      "init_cell": true,
    }

This is the same metadata used by the `init_cell nbextension`__.

__ https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/init_cell

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
solution is to provide a set of commands that first run ``nbstripout``,
then perform these operations. This is the approach of the `mmf-setup`_
package.

.. _mmf-setup: http://bitbucket.org/mforbes/mmf_setup
.. _Anaconda: https://www.continuum.io/anaconda-overview
.. _conda: http://conda.pydata.org
.. _conda-forge: http://conda-forge.github.io
.. _PyPI: https://pypi.io
