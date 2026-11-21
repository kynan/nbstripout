# How to contribute

Development of nbstripout happens on
[GitHub](https://github.com/kynan/nbstripout) -
[bug reports](https://github.com/kynan/nbstripout/issues) and
[pull requests](https://github.com/kynan/nbstripout/pulls) welcome!

## How to get started

Let's clone the repo and get into it:

    git clone https://github.com/kynan/nbstripout.git
    cd nbstripout

Then start by making a virtual environment:

    python3 -m venv .venv

Activate this environment:

    source .venv/bin/activate

NOTE: Please read [this](https://docs.python.org/3/library/venv.html#how-venvs-work) page to understand how to activate it based on your platform/shell.

For installing the required dependencies run:

    pip install -e .[dev]

Lastly to run the test suite run:

    python3 -m pytest

Bonus:
If you think the tests take a while to run try out [`pytest-xdist`](https://pytest-xdist.readthedocs.io/en/latest/), install it by running:

    pip install pytest-xdist

Then just run by using:

    python3 -m pytest -n auto

## Releasing a new version

To simplify updating the version number consistently across different files and
creating the appropriate annotated tag, we use
[bump-my-version](https://github.com/callowayproject/bump-my-version). For a new
patch release, run

    bump-my-version bump patch

and for a minor release, run

    bump-my-version bump minor

When finalizing the publish of a new release via a PR, please create a branch with the following name:

    release/*

This should activate an automatic CI job to test all MacOS python versions, since we only test partially in the lead-up to the release.

Remember to also push the release tag with `git push --tags`.

## Publishing to PyPI

This will automatically start a
[GitHub workflow for publishing to PyPI](https://github.com/kynan/nbstripout/actions/workflows/publish-to-pypi.yml),
using [PyPI's Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
([Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>)).

Explicit approval is required due to a deployment protection rule configured for
[GitHub environments](https://github.com/kynan/nbstripout/settings/environments).

The workflow has separate branches for publishing to Test PyPI and PyPI, which
can be approved separately.

## Creating the GitHub release

Create the [GitHub Release](https://github.com/kynan/nbstripout/releases) once
the tag is pushed
([GitHub documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)).

Name the release the same as the tag. For the description, copy over the section
from the Changelog. Download both the source `.tar.gz` and `.whl` from PyPI and
attach them in the binaries section. Then hit publish.

## Manual upload

**Note:** This is no longer needed and only kept for reference.

Use [twine](https://twine.readthedocs.io/en/latest/#using-twine) to upload the
new release to PyPI:

    python -m build
    twine check dist/nbstripout-0.9.2*
    twine upload -r testpypi dist/nbstripout-0.9.2*
    twine upload dist/nbstripout-0.9.2*
