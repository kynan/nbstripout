  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ nbstripout --is-installed
  [1]
  $ nbstripout --install
  $ nbstripout --is-installed
  $ nbstripout --uninstall
  $ nbstripout --is-installed
  [1]
