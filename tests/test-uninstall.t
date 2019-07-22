  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ git config filter.nbstripout.extrakeys 'spam eggs'
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ ${NBSTRIPOUT_EXE:-nbstripout} --install
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  $ ${NBSTRIPOUT_EXE:-nbstripout} --uninstall
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ git config filter.nbstripout.extrakeys
  spam eggs
