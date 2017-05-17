  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ echo -n "*.txt text" >> .git/info/attributes
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ ${NBSTRIPOUT_EXE:-nbstripout} --install
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  $ ${NBSTRIPOUT_EXE:-nbstripout} --uninstall
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ cat .git/info/attributes
  *.txt text
