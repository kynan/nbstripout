"""py.test plugin to test *.t files with cram."""

import re
import py
import pytest
import os

import cram

__version__ = '0.1'


def pytest_addoption(parser):
    """Hook up additional options."""
    group = parser.getgroup("general")
    group.addoption(
        '--cram', action='store_true',
        help="run cram on *.t files")


def pytest_collect_file(path, parent):
    """Filter files down to which ones should be checked."""
    config = parent.config
    if config.option.cram and path.ext == '.t':
        return CramItem(path, parent)


class CramError(Exception):
    """ indicates an error during cram checks. """


class CramItem(pytest.Item, pytest.File):

    def __init__(self, path, parent):
        super(CramItem, self).__init__(path, parent)
        self.add_marker("cram")

    def runtest(self):
        call = py.io.StdCapture.call
        found_errors, out, err = call(check_file, self.fspath)
        if found_errors:
            raise CramError(out, err)

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(CramError):
            return excinfo.value.args[0]
        return super(CramItem, self).repr_failure(excinfo)


class Ignorer:
    def __init__(self, ignorelines, coderex=re.compile("[EW]\d\d\d")):
        self.ignores = ignores = []
        for line in ignorelines:
            i = line.find("#")
            if i != -1:
                line = line[:i]
            try:
                glob, ign = line.split(None, 1)
            except ValueError:
                glob, ign = None, line
            if glob and coderex.match(glob):
                glob, ign = None, line
            ign = ign.split()
            if "ALL" in ign:
                ign = None
            if glob and "/" != os.sep and "/" in glob:
                glob = glob.replace("/", os.sep)
            ignores.append((glob, ign))

    def __call__(self, path):
        l = []
        for (glob, ignlist) in self.ignores:
            if not glob or path.fnmatch(glob):
                if ignlist is None:
                    return None
                l.extend(ignlist)
        return l


def check_file(path):
    """Run cram over a single file, and return the number of
    failures."""
    return cram.main([str(path)])
