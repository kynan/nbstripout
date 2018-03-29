  $ git init foobar
  Initialized empty Git repository in .* (re)
  $ cd foobar
  $ echo -n "*.txt text" >> .git/info/attributes
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ ${NBSTRIPOUT_EXE:-nbstripout} --install
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  $ git diff --no-index --no-ext-diff --unified=0 --exit-code -a --no-prefix ${TESTDIR}/test_diff.ipynb ${TESTDIR}/test_diff_output.ipynb
  $ git diff --no-index ${TESTDIR}/test_diff.ipynb ${TESTDIR}/test_diff_different.ipynb
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
  $ ${NBSTRIPOUT_EXE:-nbstripout} --uninstall
  $ ${NBSTRIPOUT_EXE:-nbstripout} --is-installed
  [1]
  $ cat .git/info/attributes
  *.txt text
  
