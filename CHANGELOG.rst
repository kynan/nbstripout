Change Log
==========

0.3.0 - 2017-02-23
------------------
* Support whitespace in repository paths (#47, #48, @ehoepfner)
* Also ignore ``collapsed`` and ``scrolled`` metadata (#34)
* Define `NO_CONVERT` for IPython <3 import (#46)

0.2.9 - 2016-11-23
------------------
* Strip `ExecuteTime` metadata (#34, #39, @jdriordan)
* Fix Python 3.5 bug: open attributes file only once (#40)
* Do not add blank line at beginning of attribute file
* Strip widget state from notebook metadata (#42)

0.2.8 - 2016-09-19
------------------
* Drop support for Python 2.6, 3.2.
* Add pip install instructions to README (#32, @oogali).
* Write trailing newline to attributes file (#36).
* Uninstall only removes ipynb filter (#37).

0.2.7 - 2016-07-30
------------------
* If you set either the ``"init_cell": true`` or
  ``"keep_output": true`` in the cell metadata, then these cells will
  not be stripped out. The former works in conjunction with the
  ``init_cell`` nbextension (#17, @mforbes).
* Fix encoding for Python 2 + 3 (#11).
* Add ``--is-installed`` and ``--status`` options (#29).
* Normalise cell output style (scroll / collapsed, #30, @kdmurray91).
* Add screencast (#31).

0.2.6 - 2016-03-13
------------------
* Use pytest-cram (#22, @mforbes).
* Add further shields to README.
* Use argparse for argument parsing.
* Add ``--attributes`` option to specify attributes file (#25).

0.2.5 - 2016-03-03
------------------
* Python 3 compatibility (#16, #21, @boeddeker).
* Windows compatibility (#18, @tt293).
* Add support for appveyor (#24).

0.2.4 - 2016-02-15
------------------
* Add ``__version__`` and ``version`` command (#12).
* Add bumpversion config.
* Add contributing guidelines (#13).

0.2.3 - 2016-02-15
------------------
* Use UTF8 writer for stdout (#11) and regression test (@geggo).
* Minor testing fixes.

0.2.2 - 2016-02-04
------------------
* Add uninstall task (#8).
* Minor testing fixes.

0.2.1 - 2016-01-27
------------------
* Add Travis CI setup (#4).
* Call decode on ``git_dir`` (#5, @michaelaye).
* Add unit tests via Cra (@mforbes).

0.2.0 - 2016-01-24
------------------
* Only process .ipynb files unless -f flag is used (@mforbes).
* Process multiple files (@mforbes).
* Add MIT License (@mforbes).

0.1.0 - not released
--------------------
* Based on Min RK's orginal but supports multiple versions of
  IPython/Jupyter and also strips the execution count.
* Add install option that fails sensibly if not in a git repository,
  does not clobber an existing attributes file and checks for an
  existing ipynb filter.
* Works with both files and stdin / stdout.
* Add README and documentation.
* Add setup.py with script entry point.
