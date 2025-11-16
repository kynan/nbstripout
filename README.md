<!-- markdownlint-disable MD030 -->
<!-- markdownlint-disable MD041 -->
[![tests](https://github.com/kynan/nbstripout/actions/workflows/tests.yml/badge.svg)](https://github.com/kynan/nbstripout/actions/workflows/tests.yml)
[![downloads](https://img.shields.io/pypi/dm/nbstripout)](https://pypi.org/project/nbstripout)
[![PyPI version](https://img.shields.io/pypi/v/nbstripout)](https://pypi.org/project/nbstripout)
[![conda-forge version](https://img.shields.io/conda/vn/conda-forge/nbstripout)](https://anaconda.org/conda-forge/nbstripout)
[![supported Python versions](https://img.shields.io/pypi/pyversions/nbstripout)](https://pypi.org/project/nbstripout)
[![Python package formats](https://img.shields.io/pypi/format/nbstripout)](https://pypi.org/project/nbstripout)
[![license](https://img.shields.io/pypi/l/nbstripout)](https://raw.githubusercontent.com/kynan/nbstripout/main/LICENSE.txt)
[![GitHub stars](https://img.shields.io/github/stars/kynan/nbstripout?style=social)](https://github.com/kynan/nbstripout/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kynan/nbstripout?style=social)](https://github.com/kynan/nbstripout/network/members)

# nbstripout: strip output from Jupyter and IPython notebooks

Reads a notebook from a file or stdin, strips output and some metadata, and
writes the "cleaned" version of the notebook to the original file or stdout.

Intended to be used as a Git filter or pre-commit hook for users who don't want
to track output in Git.

Roughly equivalent to the "Clear All Output" command in the notebook UI, but
only "visible" to Git: keep your output in the file on disk, but don't commit
the output to Git. This helps minimizing diffs and reduce file size.

Originally based on <https://gist.github.com/minrk/6176788>.

## Python 3 only

As of version 0.4.0, nbstripout supports Python 3 *only*. If you need to use
Python 2.7, install nbstripout 0.3.10:

    pip install nbstripout==0.3.10

## Screencast

This screencast demonstrates the use and working principles behind the
nbstripout utility and how to use it as a Git filter:

[![image](https://i.imgur.com/7oQHuJ5.png)](https://www.youtube.com/watch?v=BEMP4xacrVc)

## Installation

You can download and install the latest version of `nbstripout` from the Python
package index [PyPI](https://pypi.org/project/nbstripout/) as follows:

    pip install --upgrade nbstripout

When using the [Anaconda](https://www.anaconda.com/download) Python
distribution, install `nbstripout` via the [conda](https://docs.conda.io)
package manager from [conda-forge](https://conda-forge.org):

    conda install -c conda-forge nbstripout

## Usage

Strip output from IPython / Jupyter / Zeppelin notebook (modifies the file
in-place):

    nbstripout FILE.ipynb [FILE2.ipynb ...]
    nbstripout FILE.zpln

Force processing of non `.ipynb` files:

    nbstripout -f FILE.ipynb.bak

For using Zeppelin mode while processing files with other extensions use:

    nbstripout -m zeppelin -f <file.ext>

Write to stdout e.g. to use as part of a shell pipeline:

    cat FILE.ipynb | nbstripout > OUT.ipynb
    cat FILE.zpln | nbstripout -m zeppelin > OUT.zpln

or

    nbstripout -t FILE.ipynb | other-command

Do a dry run and only list which files would have been stripped:

    nbstripout --dry-run FILE.ipynb [FILE2.ipynb ...]

or

Do a verification run, which works like dry run but will fail
if any files would have been stripped:

    nbstripout --verify FILE.ipynb [FILE2.ipynb ...]

Operate on all `.ipynb` files in the current directory and subdirectories
recursively:

    find . -name '*.ipynb' -exec nbstripout {} +

Print the version:

    nbstripout --version

Show help and usage instructions:

    nbstripout --help

### Using as a Git filter

Set up the [git filter](https://git-scm.com/docs/gitattributes#_filter) and
attributes as described in the manual installation instructions below:

    nbstripout --install

Note: The filter is declared as `required`, meaning the filter *must* succeed.
Failures and misconfigurations will not simply cause the filter to be ignored.

Set up the git filter using `.gitattributes`:

    nbstripout --install --attributes .gitattributes

Specify a different path to the Python interpreter to be used for the git
filters (default is the path to the Python interpreter used when `nbstripout` is
installed). This is useful if you have Python installed in different or unusual
locations across machines, e.g. `/usr/bin/python3` on your machine vs
`/usr/local/bin/python3` in a container or elsewhere.

    nbstripout --install --python python3

Using just `python3` lets each machine find its Python itself. However, keep in
mind that depending on your setup this might not be the Python version you want
or even fail because an absolute path is required.

Set up the git filter in your global `~/.gitconfig`:

    nbstripout --install --global

Set up the git filter in your system-wide `$(prefix)/etc/gitconfig` (most
installations will require you to `sudo`):

    [sudo] nbstripout --install --system

Remove the git filter and attributes:

    nbstripout --uninstall

Remove the git filter from your global `~/.gitconfig` and attributes:

    nbstripout --uninstall --global

Remove the git filter from your system-wide `$(prefix)/etc/gitconfig` and
attributes:

    [sudo] nbstripout --uninstall --system

Remove the git filter and attributes from `.gitattributes`:

    nbstripout --uninstall --attributes .gitattributes

Check if `nbstripout` is installed in the current repository (exits with code 0
if installed, 1 otherwise):

    nbstripout --is-installed

Print status of `nbstripout` installation in the current repository and
configuration summary of filter and attributes if installed (exits with code 0
if installed, 1 otherwise):

    nbstripout --status

### Configuration files

The following table shows in which files the `nbstripout` filter and attribute
configuration is written to for given extra flags to `--install` and
`--uninstall`:

| flags                                    | filters                     | attributes                      |
| ---------------------------------------- | --------------------------- | ------------------------------- |
| none                                     | `.git/config`               | `.git/info/attributes`          |
| `--global`                               | `~/.gitconfig`              | `~/.config/git/attributes`      |
| `--system`                               | `$(prefix)/etc/gitconfig`   | `$(prefix)/etc/gitattributes`   |
| `--attributes=.gitattributes`            | `.git/config`               | `.gitattributes`                |
| `--global --attributes=.gitattributes`   | `~/.gitconfig`              | `.gitattributes`                |

### Install globally

Usually, `nbstripout` is installed per repository so you can choose where to use
it or not. You can choose to set the attributes in `.gitattributes` and commit
this file to your repository, however there is no way to have git set up the
filters automatically when someone clones a repository. This is by design, to
prevent you from executing arbitrary and potentially malicious code when cloning
a repository.

To install `nbstripout` for all your repositories such that you no longer need
to run the installation once per repository, install as follows:

    mkdir -p ~/.config/git  # This folder may not exist
    nbstripout --install --global --attributes=~/.config/git/attributes

This will set up the filters and diff driver in your `~/.gitconfig` and instruct
git to apply them to any `.ipynb` file in any repository.

Note that you need to uninstall with the same flags:

    nbstripout --uninstall --global --attributes=~/.config/git/attributes

### Install system-wide

To install `nbstripout` system-wide so that it applies to all repositories for
all users, install as follows (most installations will require you to `sudo`):

    [sudo] nbstripout --install --system

This will set up the filters and diff driver in `$(prefix)/etc/gitconfig` and
instruct git to apply them to any `.ipynb` file in any repository for any user.

Note that you need to uninstall with the same flags:

    [sudo] nbstripout --uninstall --system

### Apply retroactively

`nbstripout` can be used to rewrite an existing Git repository using
[`git filter-repo`](https://github.com/newren/git-filter-repo) to strip output
from existing notebooks. This invocation operates on all `.ipynb` files in the repo:
```bash
#!/bin/bash
git-filter-repo \
--file-info-callback "
if filename.endswith(b'.ipynb'):
    print(f'\nProcessing {filename.decode()}')
    
    import copy
    
    try:
        import nbformat
        from nbstripout import strip_output
        
        # Get the file contents using the blob_id
        contents = value.get_contents_by_identifier(blob_id)

        nb = nbformat.reads(contents.decode('utf-8'), as_version=nbformat.NO_CONVERT)
        nb_original = copy.deepcopy(nb)

        # Customize parameters as needed:
        nb_stripped = strip_output(
            nb,
            keep_output=False,
            keep_count=False,
            keep_id=False,
            extra_keys=[
                'metadata.signature',
                'metadata.widgets', 
                'cell.metadata.collapsed',
                'cell.metadata.ExecuteTime',
                'cell.metadata.execution',
                'cell.metadata.heading_collapsed',
                'cell.metadata.hidden',
                'cell.metadata.scrolled'
            ],
            drop_empty_cells=False,
            drop_tagged_cells=[],
            strip_init_cells=False,
            max_size=0
        )
        
        if nb_original != nb_stripped:
            # Convert cleaned notebook back to bytes
            new_contents = nbformat.writes(nb_stripped).encode('utf-8')
            
            print(f'  → Cleaned {filename.decode()}: {len(contents)} → {len(new_contents)} bytes')
            
            new_blob_id = value.insert_file_with_contents(new_contents)
            return (filename, mode, new_blob_id)
        else:
            print(f'  → No changes needed for {filename.decode()}')
    except Exception as e:
        print(f'Error processing {filename.decode()}: {e}')
        import traceback
        traceback.print_exc()
        # Return unchanged file on error
        return (filename, mode, blob_id)
# Return unchanged file if it's not a notebook
return (filename, mode, blob_id)
"
```

> [!WARNING]
>
> This will affect the history of the repository, so use with caution!

### Removing empty cells

Drop empty cells i.e. cells where `source` is either empty or only contains
whitespace:

    nbstripout --drop-empty-cells

### Removing [init]{.title-ref} cells

By default `nbstripout` will keep cells with `init_cell: true` metadata. To
disable this behavior use:

    nbstripout --strip-init-cells

### Removing entire cells

In certain conditions it might be handy to remove not only the output, but the
entire cell, e.g. when developing exercises.

To drop all cells tagged with "solution" run:

    nbstripout --drop-tagged-cells="solution"

The option accepts a list of tags separated by whitespace.

### Keeping some output

Do not strip the execution count/prompt number:

    nbstripout --keep-count

Do not strip outputs that are smaller that a given max size (useful for removing
only large outputs like images):

    nbstripout --max-size 1k

Do not strip the output, only metadata:

    nbstripout --keep-output

Do not reassign the cell ids to be sequential (which is the default behavior):

    nbstripout --keep-id

To mark special cells so that the output is not stripped, you can either:

1.  Set the `keep_output` tag on the cell. To do this, enable the tags toolbar
    (View > Cell Toolbar > Tags) and then add the `keep_output` tag for each
    cell you would like to keep the output for.

2.  Set the `"keep_output": true` metadata on the cell. To do this, select the
    "Edit Metadata" Cell Toolbar, and then use the "Edit Metadata" button on
    the desired cell to enter something like:

        {
          "keep_output": true,
        }

You can also keep output for an entire notebook. This is useful if you want to
strip output by default in an automated environment (e.g. CI pipeline), but want
to be able to keep outputs for some notebooks. To do so, add the option above to
the *notebook* metadata instead. (You can also explicitly remove outputs from a
particular cell in these notebooks by adding a cell-level metadata entry.)

Another use-case is to preserve initialization cells that might load customized
CSS etc. critical for the display of the notebook. To support this, we also keep
output for cells with:

    {
      "init_cell": true,
    }

This is the same metadata used by the
[init_cell nbextension](https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/init_cell).

### Stripping metadata

The following metadata is stripped by default:

-   Notebook metadata: `signature`, `widgets`
-   Cell metadata: `ExecuteTime`, `collapsed`, `execution`, `heading_collapsed`,
    `hidden`, `scrolled`

Additional metadata to be stripped can be configured via either

-   `git config (--global/--system) filter.nbstripout.extrakeys`, e.g. :

        git config --global filter.nbstripout.extrakeys '
          metadata.celltoolbar
          metadata.kernelspec
          metadata.language_info.codemirror_mode.version
          metadata.language_info.pygments_lexer
          metadata.language_info.version
          metadata.toc
          metadata.notify_time
          metadata.varInspector
          cell.metadata.heading_collapsed
          cell.metadata.hidden
          cell.metadata.code_folding
          cell.metadata.tags
          cell.metadata.init_cell'

-   the `--extra-keys` flag, which takes a space-delimited string as an
    argument, e.g. :

        --extra-keys="metadata.celltoolbar cell.metadata.heading_collapsed"

Note: Only notebook and cell metadata is currently supported and every key
specified via `filter.nbstripout.extrakeys` or `--extra-keys` must start with
`metadata.` for notebook and `cell.metadata.` for cell metadata.

You can keep certain metadata that would be stripped by default with either

-   `git config (--global/--system) filter.nbstripout.keepmetadatakeys`, e.g.:

        git config --global filter.nbstripout.keepmetadatakeys '
          cell.metadata.collapsed
          cell.metadata.scrolled'

-   the `--keep-metadata-keys` flag, which takes a space-delimited string as an
    argument, e.g.:

        --keep-metadata-keys="cell.metadata.collapsed cell.metadata.scrolled"

Note: Previous versions of Jupyter used `metadata.kernel_spec` for kernel
metadata. Prefer stripping `kernelspec` entirely: only stripping some attributes
inside `kernelspec` may lead to errors when opening the notebook in Jupyter (see
[#141](https://github.com/kynan/nbstripout/issues/141)).

### Excluding files and folders

To exclude specific files or folders from being processed by the `nbstripout`
filters, add the path and exception to your filter specifications defined in
`.git/info/attributes` or `.gitattributes`:

    docs/** filter= diff=

This will disable `nbstripout` for any file in the `docs` directory.:

    notebooks/Analysis.ipynb filter= diff=

This will disable `nbstripout` for the file `Analysis.ipynb` located in the
`notebooks` directory.

To check which attributes a given file has with the current config, run:

    git check-attr -a -- path/to/file

For a file to which the filter applies you will see the following:

    $ git check-attr -a -- foo.ipynb
    foo.ipynb: diff: ipynb
    foo.ipynb: filter: nbstripout

For a file in your excluded folder you will see the following:

    $ git check-attr -a -- docs/foo.ipynb
    foo.ipynb: diff:
    foo.ipynb: filter:

## Manual filter installation

Set up a git filter and diff driver using nbstripout as follows:

    git config filter.nbstripout.clean '/path/to/nbstripout'
    git config filter.nbstripout.smudge cat
    git config filter.nbstripout.required true
    git config diff.ipynb.textconv '/path/to/nbstripout -t'

This will add a section to the `.git/config` file of the current repository.

If you want the filter to be installed globally for your user, add the
`--global` flag to the `git config` invocations above to have the configuration
written to your `~/.gitconfig` and apply to all repositories.

If you want the filter to be installed system-wide, add the `--system` flag to
the `git config` invocations above to have the configuration written to
`$(prefix)/etc/gitconfig` and apply to all repositories for all users.

Create a file `.gitattributes` (if you want it versioned with the repository) or
`.git/info/attributes` (to apply it only to the current repository) with the
following content:

    *.ipynb filter=nbstripout
    *.ipynb diff=ipynb

This instructs git to use the filter named `nbstripout` and the diff driver
named `ipynb` set up in the git config above for every `.ipynb` file in the
repository.

If you want the attributes be set for `.ipynb` files in any of your git
repositories, add those two lines to `~/.config/git/attributes`. Note that this
file and the `~/.config/git` directory may not exist.

If you want the attributes be set for `.ipynb` files in any git repository on
your system, add those two lines to `$(prefix)/etc/gitattributes`. Note that
this file may not exist.

## Using `nbstripout` as a pre-commit hook

[pre-commit](https://pre-commit.com) is a framework for managing git
[pre-commit hooks](https://git-scm.com/docs/githooks).

Once you have [pre-commit](https://pre-commit.com) installed, add the following
to the `.pre-commit-config.yaml` in your repository:

    repos:
    - repo: https://github.com/kynan/nbstripout
      rev: 0.8.2
      hooks:
        - id: nbstripout

Then run `pre-commit install` to activate the hook.

When passing parameters to the hook, be aware that arguments with spaces such as
`--extra-keys` need to be quoted as a whole:

    repos:
    - repo: https://github.com/kynan/nbstripout
      rev: 0.8.2
      hooks:
        - id: nbstripout
          args: ['--extra-keys=metadata.celltoolbar cell.metadata.heading_collapsed']

> [!WARNING]
>
> In this mode, `nbstripout` is used as a git hook to strip any `.ipynb` files
> before committing. This also modifies your working copy!
>
> In its regular mode, `nbstripout` acts as a filter and only modifies what git
> gets to see for committing or diffing. The working copy stays intact.

## Troubleshooting

### Known issues

Certain Git workflows are not well supported by `nbstripout`:

-   Local changes to notebook files that are made invisible to Git due to the
    `nbstripout` filter do still cause conflicts when attempting to sync
    upstream changes (`git pull`, `git merge` etc.). This is because Git has no
    way of resolving a conflict caused by a non-stripped local file being merged
    with a stripped upstream file.  Addressing this issue is out of scope for
    `nbstripout`. Read more and find workarounds in
    [#108](https://github.com/kynan/nbstripout/issues/108).

### Show files processed by nbstripout filter

Git has [no builtin support](https://stackoverflow.com/a/52065333/396967) for
listing files a clean or smudge filter operates on. As a workaround, change the
setup of your filter in `.git/config`, `~/.gitconfig` or
`$(prefix)/etc/gitconfig` as follows to see the filenames either filter operates
on:

    [filter "nbstripout"]
        clean  = "f() { echo >&2 \"clean: nbstripout $1\"; nbstripout; }; f %f"
        smudge = "f() { echo >&2 \"smudge: cat $1\"; cat; }; f %f"
        required = true
