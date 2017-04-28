  $ bash -c "diff <( ${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb ) <( ${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb )"
  $ bash -c "diff <( ${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb ) <( ${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_different.ipynb )"
  (.*) (re)
  <     "print(\"aou\")"
  ---
  (.*\"print\(\\\"aou now it is different\\\"\)\") (re)
  [1]
