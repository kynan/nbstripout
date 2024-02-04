# How to contribute

Development of nbstripout happens on
[GitHub](https://github.com/kynan/nbstripout) -
[bug reports](https://github.com/kynan/nbstripout/issues) and
[pull requests](https://github.com/kynan/nbstripout/pulls) welcome!

# Releasing a new version

To simplify updating the version number consistently across different files and
creating the appropriate annotated tag, we use
[bump-my-version](https://github.com/callowayproject/bump-my-version). For a new
patch release, run

    bump-my-version bump patch

and for a minor release, run

    bump-my-version bump minor

Remember to also push the release tag with `git push --tags`.

Use [twine](https://twine.readthedocs.io/en/latest/#using-twine) to upload the
new release to PyPI:

    python -m build
    twine check dist/nbstripout-0.6.2*
    twine upload -r testpypi dist/nbstripout-0.6.2*
    twine upload dist/nbstripout-0.6.2*
