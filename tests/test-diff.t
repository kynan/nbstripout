  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  9c9
  <     "print u\"äöü\""
  ---
  >     "print u\"äöü now it is different \""

  
