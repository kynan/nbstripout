# Changelog

## 0.9.0 - 2026-01-17

- Add GitHub Action checking that output is stripped (@lagamura, #205, #207)
- Add `--drop-output-type`, `--keep-output-type` flags (@rgeorgi, #175, #204)
- Drop support for Python 3.8 and 3.9, add support for Python 3.13 and 3.14
- Migrate to pyproject.toml, remove setup.py and setup.cfg

## 0.8.2 - 2025-11-16

- Preserve Windows CRLF file endings in output file (#202)
- Prevent `BrokenPipeError` when flushing the output (@blaketastic2, #203)
- README: update usage instructions for git-filter-repo (@fztrevisan, #201)
- README: add note about argument quoting for pre-commit hook (#119).
- Use ruff for code formatting
- Add type annotations

## 0.8.1 - 2024-11-17

- In dry run mode, only print output if there would have been a change (#152).
- Declare git filter to be `required` when installing, such that it *must*
    succeed (#191).

## 0.8.0 - 2024-11-03

- Adds `--verify` flag, similar to `--dry-run` but returning 1 if any
  affected files would have changed (@jspaezp, #153, #195).
- Adds script to apply `nbstripout` retroactively using `git-filter-repo` to
  README (@LunarLanding @tokleine, #194 #197).
- Documents nbstripout on all files in the current directory and
  subdirectories recursively (#127).
- Accepts notebooks without `nbformat` version specified.
- Improves test coverage.

## 0.7.1 - 2024-02-04

- Fix regression where input file was truncated before reading (#190).

## 0.7.0 - 2024-02-04

- **This release has been yanked from PyPI due to a major regression (#190).**
- Drop support for Python 3.7 (end of life 2023-06-27), require Python 3.8.
- Add support for Python 3.12.
- Drop backwards compability with IPython.nbformat for IPython <4.
- Rename cell ids to be sequential by default. Disable by passing `--keep-id`
  (@JasonJooste, #184).
- Improve documentation for notebook and cell metadata stripping (#187).
- Switch from pytest-flake8 to pytest-ruff.
- Convert all text assets from rST to Markdown format.

## 0.6.2 - 2024-02-03

- Add `--python` option for `nbstripout --install` to allow overriding the
  Python interpreter specified in `.git/config` (@nobodyinperson, #181 #182).
- Add option `--keep-metadata-keys` to keep specific metadata keys that are
  stripped by default (@davidxia, #78 #177).
- Replace [Cram](https://bitheap.org/cram/) as test runner for integration
  tests with a custom framework which also supports testing on Windows
  (@arobrien, #176 #178).
- Use `SystemExit` instead of `sys.exit` and do not exit from functions
  (@janosh, #173).

## 0.6.1 - 2022-09-24

- Removed `setup_requires` and `tests_require` and no longer rely on
  `pytest-runner` for test execution but invoke `pytest` directly (#168).

## 0.6.0 - 2022-07-24

- Support for stripping init cells (@Pugio, #157).
- Added `--drop-tagged-cells="some tags"` option (@boun, #161).
- Renamed `--strip-empty-cells` to `--drop-empty-cells`.
- Dropped support for Python 3.5, added support for Python 3.10.

## 0.5.0 - 2021-06-28

- Support only stripping outputs larger than a given size (@cjblocker, #135).
- Support stripping output from Zeppelin Notebooks (@ankitrokdeonsns, #130).
- Switch CI to GitHub actions (#151).
- Support attributes file without leading path component (#155).

## 0.4.0 - 2021-04-25

- Add support for system wide installation, `--system` flag
  (@PLPeeters, #149).
- Use `~` instead of `$HOME` for config dir (#136).
- Document stripping kernelspec (#141).
- Add support for removing empty cells (#131).
- Create directory for attributes file if needed (#139).
- Add support for stripping metadata keys containing periods
  (@baldwint, #143).
- Strip collapsible headings by default (@rpytel1, #142).

## 0.3.10 - 2021-04-24

- Python 2.7 only release, to make `pip install nbstripout` work in Python 2.7.
  Previously, this was picking up 0.3.8 which is *not* Python 2.7 compatible.
- Drop Python 3.4 support, add support for Python 3.7, 3.8.
- Windows compatibility: `""` quote Python interpreter path
  (@fcollonval, #115).
- Add `--dry-run` flag (#122).
- Support specifying `keep_output` as a cell tag (@scottcode, #117).

## 0.3.9 - 2020-06-28

- Document Python 3 support only. Fail to install on Python 2
  (@casperdcl, #128)
- Drop support for Python 3.4 (end of life 2019-03-18).
- Ignore warnings from `nbformat.{read,write}`.
- Support nbformat 2 notebooks without cell metadata.
- Add `--extra-keys` flag to pass extra keys to strip (#119).
- Apply pre-commit hook to files of type Jupyter.

## 0.3.8 - 2020-06-06

- Drop Python 2 support.
- Windows compatibility: `""` quote Python interpreter path
  (@fcollonval, #115).
- Add `--dry-run` flag (#122).
- Support specifying `keep_output` as a cell tag (@scottcode, #117).
- Improved error handling for the case where git is not installed (#124).
- Nicer error message when input file is not found.
- Use universal newlines without conversion (@ooiM, #110, #126).
- Strip execution timing from cell metadata (#118).
- Document which metadata is stripped by default.
- Make `--global` commands work outside of git repository (#123).

## 0.3.7 - 2020-01-05

- Notebook-level `keep_output` (@jonashaag, #112).
- Fix quoting of Python path and call module entrypoint (@jonashaag, #111).
- Do not run `git add` in pre-commit hook (@SimonBiggs, #106).
- Troubleshooting instructions (#65).
- Exclusion instructions for folders (@jraviotta, #104).
- Only remove `filter.nbstripout.{clean,smudge}` on `--uninstall`.
- Remove unnecessary `filter.nbstripout.required` config setting.
- pre-commit configuration (@Ohjeah, #79).

## 0.3.6 - 2019-07-18

- Document global installation in README (#100).
- Document how to exclude folders in README (#99).
- Expand `~` when looking up attributes file.
- Add `--global` flag for `--install` / `--uninstall` to write the filter
  config to `~/.gitconfig` (#98).

## 0.3.5 - 2019-04-02

- Make nbstripout package executable and fix regression (#94).
- Add package docstring.

## 0.3.4 - 2019-03-26

- Fix `WindowsError` not defined on POSIX systems (#90).
- Add support for blacklisting custom metadata fields (@casperdcl, #92).

## 0.3.3 - 2018-08-04

- Distribute tests in source package (@jluttine, #73 #76).
- Fix git diff tests for newer Git versions (@jluttine, #74 #76).
- Install full path for diff.ipynb.textconv (@ibressler, #68 #82).
- Make sure sys.stdin is not None before reading from it (@ibressler, #68 #82).

## 0.3.2 - 2018-07-09

- Gracefully deal with empty/malformed input (#66).
- Add Code of Conduct (#63).
- Add MANIFEST.in (#64).
- Document `git filter-branch` use case in README (@belteshassar, #28).
- Flush output when using `-t` (@tnilanon, #67).
- Add `nbformat` and `setuptools >= 30` to `setup_requires` (@tnilanon, #67).
- Use `travis_retry` (@tnilanon, #67).
- Drop support for Python 3.3 (no longer supported by setuptools).

## 0.3.1 - 2017-07-30

- Add option `-t`/`--textconv` to write to stdout e.g. for use as diff filter
  (@utsekaj42, #53).
- Flush output stream after write (@reidpr, #55).
- Add options `--keep-count` and `--keep-output` to no strip execution counts
  and output (@jpeacock29, #56).
- Fix shell pipeline documentation (@psthomas, #59).
- Catch `WindowsError` when `git` is not found in PATH (@bdforbes, #62).

## 0.3.0 - 2017-02-23

- Support whitespace in repository paths (@ehoepfner, #47 #48).
- Also ignore `collapsed` and `scrolled` metadata (#34).
- Define `NO_CONVERT` for IPython <3 import (#46).

## 0.2.9 - 2016-11-23

- Strip `ExecuteTime` metadata (@jdriordan, #34 #39).
- Fix Python 3.5 bug: open attributes file only once (#40).
- Do not add blank line at beginning of attribute file.
- Strip widget state from notebook metadata (#42).

## 0.2.8 - 2016-09-19

- Drop support for Python 2.6, 3.2.
- Add pip install instructions to README (@oogali, #32).
- Write trailing newline to attributes file (#36).
- Uninstall only removes ipynb filter (#37).

## 0.2.7 - 2016-07-30

- If you set either the `"init_cell": true` or `"keep_output": true` in the
  cell metadata, then these cells will not be stripped out. The former works in
  conjunction with the `init_cell` nbextension (@mforbes, #17).
- Fix encoding for Python 2 + 3 (#11).
- Add `--is-installed` and `--status` options (#29).
- Normalise cell output style, setting `scroll` and `collapsed` to False
  (@kdmurray91, #30).
- Add screencast (#31).

## 0.2.6 - 2016-03-13

- Use pytest-cram (@mforbes, #22).
- Add further shields to README.
- Use argparse for argument parsing.
- Add `--attributes` option to specify attributes file (#25).

## 0.2.5 - 2016-03-03

- Python 3 compatibility (@boeddeker, #16 #21).
- Windows compatibility (@tt293, #18).
- Add support for appveyor (#24).

## 0.2.4 - 2016-02-15

- Add `__version__` and `version` command (#12).
- Add bumpversion config.
- Add contributing guidelines (#13).

## 0.2.3 - 2016-02-15

- Use UTF8 writer for stdout and regression test (@geggo, #11).
- Minor testing fixes.

## 0.2.2 - 2016-02-04

- Add uninstall task (#8).
- Minor testing fixes.

## 0.2.1 - 2016-01-27

- Add Travis CI setup (#4).
- Call decode on `git_dir` (@michaelaye, #5).
- Add unit tests via Cram (@mforbes).

## 0.2.0 - 2016-01-24

- Only process .ipynb files unless -f flag is used (@mforbes).
- Process multiple files (@mforbes).
- Add MIT License (@mforbes).

## 0.1.0 - not released

- Based on Min RK's original [gist](https://gist.github.com/minrk/6176788) but
  supports multiple versions of IPython/Jupyter and also strips execution count.
- Add install option that fails sensibly if not in a git repository, does not
  clobber an existing attributes file and checks for an existing ipynb filter.
- Works with both files and stdin / stdout.
- Add README and documentation.
- Add setup.py with script entry point.
