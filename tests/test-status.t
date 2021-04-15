  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ ${NBSTRIPOUT_EXE:-nbstripout} --status
  nbstripout is not installed in repository .* (re)
  [1]
  $ ${NBSTRIPOUT_EXE:-nbstripout} --install
  $ ${NBSTRIPOUT_EXE:-nbstripout} --status
  nbstripout is installed in repository .* (re)
  \s* (re)
  Filter:
    clean = .* -m nbstripout (re)
    smudge = cat
    diff= .* -m nbstripout -t (re)
    extrakeys=\s* (re)
  \s* (re)
  Attributes:
    *.ipynb: filter: nbstripout
  \s* (re)
  Diff Attributes:
    *.ipynb: diff: ipynb
  $ ${NBSTRIPOUT_EXE:-nbstripout} --uninstall
  $ ${NBSTRIPOUT_EXE:-nbstripout} --status
  nbstripout is not installed in repository .* (re)
  [1]
