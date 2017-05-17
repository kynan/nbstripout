  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ echo -n "*.txt text" >> .git/info/attributes
  $ nbstripout --is-installed
  [1]
  $ nbstripout --install
  $ nbstripout --is-installed
  $ git diff --no-ext-diff --unified=0 --exit-code -a --no-prefix ${TESTDIR}/test_diff.ipynb ${TESTDIR}/test_diff_output.ipynb 
  [1]
  $ git diff ${TESTDIR}/test_diff.ipynb ${TESTDIR}/test_diff_different.ipynb 
  (diff --git.*) (re)
  (index .*) (re)
  (--- .*test_diff.ipynb) (re)
  (\+\+\+ .*test_diff_different.ipynb) (re)
  @@ -6,7 +6,7 @@
      "metadata": {},
      "outputs": [],
      "source": [
  -    "print(\"aou\")"
  +    "print(\"aou now it is different\")"
      ]
     }
    ],
  [1]
  $ nbstripout --uninstall
  $ nbstripout --is-installed
  [1]
  $ cat .git/info/attributes
  *.txt text
  
