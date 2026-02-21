# How to contribute

Development of nbstripout happens on
[GitHub](https://github.com/kynan/nbstripout) -
[bug reports](https://github.com/kynan/nbstripout/issues) and
[pull requests](https://github.com/kynan/nbstripout/pulls) welcome!

## Releasing a new version

To simplify updating the version number consistently across different files and
creating the appropriate annotated tag, we use
[bump-my-version](https://github.com/callowayproject/bump-my-version). For a new
patch release, run

    bump-my-version bump patch

and for a minor release, run

    bump-my-version bump minor

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

## Manual upload

**Note:** This is no longer needed and only kept for reference.

Use [twine](https://twine.readthedocs.io/en/latest/#using-twine) to upload the
new release to PyPI:

    python -m build
    twine check dist/nbstripout-0.9.1*
    twine upload -r testpypi dist/nbstripout-0.9.1*
    twine upload dist/nbstripout-0.9.1*
