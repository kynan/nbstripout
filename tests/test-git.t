  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ echo -n "*.txt text" >> .git/info/attributes
  $ nbstripout --is-installed
  [1]
  $ nbstripout --install
  $ nbstripout --is-installed
  $ nbstripout --uninstall
  $ nbstripout --is-installed
  [1]
  $ cat .git/info/attributes
  *.txt text
